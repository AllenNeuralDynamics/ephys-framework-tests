import spikeinterface as si
import spikeinterface.toolkit as st
from spikeinterface.toolkit import preprocessing

# instance dependent (especcially n_jobs)
# for many jobs, it's better to keep chunk duration quite small
job_kwargs = dict(n_jobs=40, chunk_duration="1s", progress_bar=True)


# define some preprocessing params
# IMO, we should have a 1-to-1 correspondence between SI functions and their kwargs

# TODO Josh is fixing the phase_shift (let's skip it for now)
# TODO we have now several motion-correction algos that can be applied here for drift removal
# (more computationally expensive at the moment)
preprocessing_params = dict(
    "bandpass_filter": dict(freq_min=300.0,
                            freq_max=6000.0,
                            margin_ms=5.0),
    "common_reference": dict(reference='global',
                             operator='median'),
)


# these are used by zarr to remotely read-write from gcloud
token = "/home/alessio/.config/gcloud/legacy_credentials/alessiop.buccino@gmail.com/adc.json"
storage_options={"token": token}

# define bucket and session name
bucket = "gcs://aind-transfer-service-test/zarr-test-folder"
session = "595262_2022-02-21_15-18-07"

# ideally we would loop trough the streams in the bucket/session folder.
# for now, we fix one recording
zarr_path_gcloud = "gcs://aind-transfer-service-test/zarr-test-folder/595262_2022-02-21_15-18-07"

# read recording
recording = si.read_zarr("path-to-zarr.zarr")

recording_preprocessed = si.bandpass_filter(recording, 
                                            **preprocessing_params["bandpass_filter"])

recording_preprocessed = si.common_reference(recording, 
                                             **preprocessing_params["common_reference"])

# save in the output folder (for CodeOcean) or into a bucket
# note that also the preprocessed data could be compressed
rec_saved = recording_preprocessed.save(folder="output/preprocessed",
                                        **job_kwargs)
# done preprocessing node
