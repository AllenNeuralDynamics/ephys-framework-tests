from pathlib import Path
import spikeinterface as si
import spikeinterface.extractors as se
import spikeinterface.toolkit as st
import neo
import numpy as np
import time
import sys
import os
from numcodecs import Blosc

si_scripts_folder = Path(__file__).parent.parent / "spikeinterface_scripts"
sys.path.append(str(si_scripts_folder))

# TODO maybe move this to spikeinterface?
from utils import get_median_and_lsb

# base gcloud bucket
bucket = "gcs://aind-transfer-service-test/zarr-test-folder"

# define input OE folder (either NP1 or NP2)
data_base_folder = Path("/home/alessio/Documents/data/allen/npix-open-ephys")
# session
session = "595262_2022-02-21_15-18-07"

# this assumes you have a GOOGLE_APPLICATION_CREDENTIALS env
gcloud_token = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", None)
if gcloud_token:
    # TODO fix download request 
    token = gcloud_token
    storage_options={"token": token}
else:
    raise Exception("No credentials found!")


# define compressor
compressor = Blosc(cname="Zstd", clevel=9, shuffle=Blosc.BITSHUFFLE)

oe_folder = data_base_folder / session

# we have to first access the different streams (i.e., different probes)
io = neo.rawio.OpenEphysBinaryRawIO(oe_folder)
io._parse_header()
streams = io.header['signal_streams']

# now we can save one file per stream
for stream_name, stream_id in streams:
    print(f"Compressing stream {stream_name}")
    rec_oe = se.read_openephys(oe_folder, stream_id=stream_id)

    dtype = rec_oe.get_dtype()

    lsb_value, median_values = get_median_and_lsb(rec_oe, num_random_chunks=2)

    # median correction
    rec_to_compress = st.scale(rec_oe, gain=1., offset=-median_values, dtype=dtype)
    rec_to_compress = st.scale(
        rec_to_compress, gain=1. / lsb_value, dtype=dtype)
    rec_to_compress.set_channel_gains(rec_to_compress.get_channel_gains() * lsb_value)

    zarr_path = f"{bucket}/{oe_folder.name}/compressed/{stream_name}.zarr"

    t_start = time.perf_counter()
    rec_gcloud = rec_to_compress.save(format="zarr", zarr_path=zarr_path, storage_options=storage_options,
                                      progress_bar=True, chunk_duration="1s", n_jobs=1)
    t_stop = time.perf_counter()
    elapsed_time = np.round(t_stop - t_start, 2)

    xRT = rec_oe.get_total_duration() / elapsed_time
    print(f"Stream {stream_name} took {xRT} real-time")
    

# Call gsutil to copy the Open-Ephys folder except .dat files
local_src = str(oe_folder)
bucket_dst = f"{bucket}/{session}/open-ephys"
cmd = f"gsutil rsync -r -x \".*\.dat$\" {local_src} {bucket_dst}"
os.system(cmd)

# TODO: Upload videos in f"{bucket}/{session}/behavior"

# TODO: Upload metadata.json/yaml in f"{bucket}/{session}/"
