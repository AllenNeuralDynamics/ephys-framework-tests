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
bucket = "aind-transfer-service-test/zarr-test-folder"
gcs_path = f"gcs://{bucket}"

# define input OE folder (either NP1 or NP2)
data_base_folder = Path("/home/alessio/Documents/data/allen/npix-open-ephys")
# session
session = "595262_2022-02-21_15-18-07"

# define a localt tmp folder
local_tmp_folder = Path("tmp")


# this assumes you have a GOOGLE_APPLICATION_CREDENTIALS env
gcloud_token = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", None)
if gcloud_token:
    # TODO fix download request 
    token = gcloud_token
    # storage_options={"token": token}
    storage_options={"token": None}
else:
    raise Exception("No credentials found!")


# define compression options
compressor = Blosc(cname="zstd", clevel=9, shuffle=Blosc.BITSHUFFLE)
print(f"Compressor: {compressor}")

chunk_duration = "1s"
n_jobs = 20

job_kwargs = dict(n_jobs=n_jobs, chunk_duration=chunk_duration, progress_bar=True)

# we have to first access the different streams (i.e., different probes)
oe_folder = data_base_folder / session
io = neo.rawio.OpenEphysBinaryRawIO(oe_folder)
io._parse_header()
streams = io.header['signal_streams']

print(f"Found {len(streams)} streams in session {session}")

zarr_paths = []
# now we can save one file per stream
for stream_name, stream_id in streams:
    print(f"Compressing stream '{stream_name}'")
    rec_oe = se.read_openephys(oe_folder, stream_id=stream_id)
    dtype = rec_oe.get_dtype()

    lsb_value, median_values = get_median_and_lsb(rec_oe, num_random_chunks=2)

    # median correction
    rec_to_compress = st.scale(rec_oe, gain=1., offset=-median_values, dtype=dtype)
    rec_to_compress = st.scale(
        rec_to_compress, gain=1. / lsb_value, dtype=dtype)
    rec_to_compress.set_channel_gains(rec_to_compress.get_channel_gains() * lsb_value)
    
    # apparently Gcloud doesn't like '#'
    stream_name = stream_name.strip("/").replace("#", "-")

    zarr_path = local_tmp_folder / session / "{stream_name}.zarr".replace(" ", "")
    print(f"Local destination: {zarr_path}")

    # save locally and upload later
    t_start = time.perf_counter()
    rec_local= rec_to_compress.save(format="zarr", zarr_path=zarr_path, 
                                      compressor=compressor, **job_kwargs)
    t_stop = time.perf_counter()
    elapsed_time = np.round(t_stop - t_start, 2)
    
    cr = rec_local.get_annotation("compression_ratio")

    xRT = rec_oe.get_total_duration() / elapsed_time
    print(f"Stream '{stream_name}':\n\tcompression speed: {xRT} real-time\n\tcompression ratio: {cr}")
    zarr_paths.apprnd(zarr_path)


# Call gsutil to copy the zarr-folders folder except .dat files
bucket_dst = f"{bucket}/{session}/compressed"
for zarr_path in zarr_paths:
    local_src = zarr_path
    cmd = f"gsutil rsync {local_src} {bucket_dst}"

# # Call gsutil to copy the Open-Ephys folder except .dat files
# local_src = str(oe_folder)
# bucket_dst = f"{bucket}/{session}/open-ephys"
# cmd = f"gsutil rsync -r -x \".*\.dat$\" {local_src} {bucket_dst}"
# os.system(cmd)

# TODO: Upload videos in f"{bucket}/{session}/behavior"

# TODO: Upload metadata.json/yaml in f"{bucket}/{session}/"
