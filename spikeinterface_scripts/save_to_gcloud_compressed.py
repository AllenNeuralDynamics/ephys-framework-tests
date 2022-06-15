from pathlib import Path
import spikeinterface.full as si
import neo
import numpy as np
import time

# TODO maybe move this to spikeinterface?
from utils import get_median_and_lsb

# here goes the gcloud token (might not be needed if running from the cloud)
# these are used by zarr to remotely read-write from gcloud
token = "/home/alessio/.config/gcloud/legacy_credentials/alessiop.buccino@gmail.com/adc.json"
storage_options={"token": token}


# define input OE folder (either NP1 or NP2)
data_base_folder = Path("/home/alessio/Documents/data/allen/npix-open-ephys")
# session
session = "595262_2022-02-21_15-18-07"
oe_folder = data_base_folder / session

# base gcloud bucket
bucket = "gcs: // aind-transfer-service-test/zarr-test-folder"

# we have to first access the different streams (i.e., different probes)
io = neo.rawio.OpenEphysBinaryRawIO(oe_folder)
io._parse_header()
streams = io.header['signal_streams']

# now we can save one file per stream
for stream_name, stream_id in streams:
    rec_oe = si.read_openephys(oe_folder, stream_id=stream_id)
    print(rec_oe)
    print(rec_oe.get_probe())

    dtype = rec_oe.get_dtype()

    lsb_value, median_values = get_median_and_lsb(rec_oe, num_random_chunks=2)

    # median correction
    rec_to_compress = si.scale(rec_oe, gain=1., offset=-median_values, dtype=dtype)
    rec_to_compress = si.scale(rec_oe, gain=1. / lsb_value, dtype=dtype)
    rec_to_compress.set_channel_gains(rec_to_compress.get_channel_gains() * lsb_value)

    zarr_path = f"{bucket}/{oe_folder.name}/{stream_name}_{stream_id}.zarr"

    t_start = time.perf_counter()
    rec_gcloud = rec_to_compress.save(format="zarr", zarr_path=zarr_path, storage_options=storage_options,
                                      progress_bar=True, chunk_duration="1s", n_jobs=1)
    t_stop = time.perf_counter()
    elapsed_time = np.round(t_stop - t_start, 2)

    xRT = rec_oe.get_total_duration() / elapsed_time
    print(f"Stream {stream_name} took {xRT} real-time")
