from pathlib import Path
from threading import local
import spikeinterface as si
import spikeinterface.extractors as se
import spikeinterface.toolkit as st
import spikeinterface.sorters as ss
import neo
import numpy as np
import time
import sys
import os


# define params
preprocessing_params = dict(
    bandpass_filter=dict(freq_min=300.0,
                         freq_max=6000.0,
                         margin_ms=5.0),
    common_reference=dict(reference='global',
                          operator='median'),
)

sorter_name = "kilosort2_5"
sorter_params = ss.get_default_sorter_params(sorter_name)

print(sorter_params)

# base gcloud bucket
bucket = "gcs://aind-transfer-service-test/zarr-test-folder"
local_output_folder = Path("sorting_outputs")
local_output_folder.mkdir(exist_ok=True)

# define input OE folder (either NP1 or NP2)
data_base_folder = Path("/home/alessio/Documents/data/allen/npix-open-ephys")
# session
session = "595262_2022-02-21_15-18-07"

oe_folder = data_base_folder / session

# we have to first access the different streams (i.e., different probes)
io = neo.rawio.OpenEphysBinaryRawIO(oe_folder)
io._parse_header()
streams = io.header['signal_streams']

# now we can save one file per stream
for stream_name, stream_id in streams:
    print(f"Compressing stream {stream_name}")
    recording = se.read_openephys(oe_folder, stream_id=stream_id)

    # preprocess
    recording_preprocessed = si.bandpass_filter(recording, 
                                                **preprocessing_params["bandpass_filter"])
    
    # TODO: waiting for Josh's patch
    # recording_preprocessed = si.phase_shift(recording)

    recording_preprocessed = si.common_reference(recording, 
                                                 **preprocessing_params["common_reference"])
        
    
    # spike sort in docker (with docker_image=True the latest available image for the sorter is used)
    sorting = ss.run_sorter(sorter_name=sorter_name, recording=recording_preprocessed,
                            output_folder=f"tmp_{session}_{sorter_name}", delete_output_folder=True,
                            docker_image=True, **sorter_params)
    
    print(f"{sorter_name} output on {session}-{stream_name}: {sorting}")
    
    # save output
    sorting_saved = sorting.save(folder=local_output_folder / f"{sorter_name}_{stream_name}")
    

# Call gsutil to copy the Open-Ephys folder except .dat files
for sorting_folder in local_output_folder.iterdir():
    if sorting_folder.is_dir():
        local_src = str(sorting_folder)
        bucket_dst = f"{bucket}/{session}/sorting_output/{sorting_folder.name}"
        cmd = f"gsutil rsync -r -x \".*\.dat$\" {local_src} {bucket_dst}"
        os.system(cmd)
