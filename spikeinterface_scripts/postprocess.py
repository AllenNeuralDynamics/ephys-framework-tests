import spikeinterface as si
from spikeinterface.postprocessing import (compute_spike_amplitudes, compute_spike_amplitudes, 
                                           compute_principal_components, compute_spike_locations,
                                           compute_template_similarity, calculate_template_metrics,
                                           compute_correlograms, get_template_channel_sparsity)
from spikeinterface.qualitymetrics import get_quality_metric_list, get_quality_pca_metric_list, compute_quality_metrics

####################################### IMAGE ###############################################
#
# - base-spikeinterface-image
#
##############################################################################################


####################################### INPUTS ###############################################
#
# - "input/preprocessed" folder from "preprocess" node
# - "input/{sorter_name}_output" from spikesort node
#
##############################################################################################

instance_params = dict(n_cpus=40, total_ram="128G")

# instance dependent (especially n_jobs)
# for many jobs, it's better to keep chunk duration quite small
job_kwargs = dict(n_jobs=instance_params["n_cpus"], chunk_duration="1s", progress_bar=True)
sorter_name = "kilosort2_5"


postprocessing_params = dict(
    waveforms=dict(ms_before=2,
                   ms_after=5,
                   max_spikes_per_unit=1000),
    sparsity=dict(method="radius", radius_um=50),
    ccg=dict(window_ms=100, bin_ms=1),
    localization=dict(method="monopolar_triangulation", 
                      method_kwargs={"raidus": 100}),
    principal_components=dict(mode="by_channel_local", 
                              n_components=5,
                              whiten=True),
    template_metrics=dict(metric_names=['peak_to_valley', 'peak_trough_ratio', 'half_width', 'repolarization_slope',
                                        'recovery_slope'],
                          upsample=10),
    quality_metrics=dict(metric_names=['num_spikes', 'firing_rate', 'presence_ratio', 'snr',
                                       'isi_violation', 'amplitude_cutoff', 'nearest_neighbor'])
)

# read preprocessed recording and sorted output
recording = si.load_extractor("input/preprocessed")
sorting = si.load_extractor(f"input/{sorter_name}_output")

# compute waveforms (note - the waveform folder will be the output of the node - in next release)
we = si.extract_waveforms(recording, sorting, folder="outputs/postprocessing",
                          **postprocessing_params["waveforms"], **job_kwargs)

# first we calculate sparse channels for each sorted unit
sparsity = get_template_channel_sparsity(we, **postprocessing_params["sparsity"])

# the following functions are WaveformExtensions, and they append their respective data to the waveform folder

# ccgs
ccgs, bins = si.compute_correlograms(sorting=we.sorting, symmetrize=True,
                                     **postprocessing_params["ccg"])

# spike localization
locs = si.compute_spike_locations(we, outputs="by_unit", load_if_exists=True, 
                                  **postprocessing_params["localization"], **job_kwargs)

# spike amplitudes
amplitudes = si.compute_spike_amplitudes(we, outputs="by_unit", load_if_exists=True, 
                                         **job_kwargs)

# similarity
similarity = si.compute_template_similarity(we)

# template metrics
tm = si.calculate_template_metrics(we, **postprocessing_params["template_metrics"])

# compute PC
pc = si.compute_principal_components(we, **postprocessing_params["principal_components"], **job_kwargs)

# quality metrics
qm = si.compute_quality_metrics(we, sparsity=sparsity, 
                                **postprocessing_params["quality_metrics"], **job_kwargs)

# unit locations
unit_locations = si.localize_units(we, output="dict", **postprocessing_params["sparsity"])


####################################### OUTPUTS ###############################################
#
# - "output/postprocessing" folder contains all postprocessed data
#
##############################################################################################