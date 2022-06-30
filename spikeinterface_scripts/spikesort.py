import spikeinterface as si
import spikeinterface.sorters as ss


####################################### IMAGE ###############################################
#
# - from base-sorter-image (see https://hub.docker.com/u/spikeinterface) + SI dependencies
#
##############################################################################################

####################################### INPUTS ###############################################
#
# - "input/preprocessed" folder from "preprocess" node
#
##############################################################################################

# the capsule/image will determine which sorter to run 
# (because it will be the only one installed in the container)
sorter_name = "kilosort2_5"

# we might also use the parallel capabilities to do some parameter search
sorter_params = {}

preprocessed_folder = "inputs/preprocessed"

# load the preprocessed folder from bucket/codocean output
recording_preprocessed = si.load_extractor(preprocessed_folder)

# run spike sorting 
# NOTE: we don't use the docker/singularity mechanism here because the sorter is installed "locally"
sorting = ss.run_sorter(sorter_name=sorter_name, recording=recording_preprocessed,
                        output_folder=f"tmp_{sorter_name}", delete_output_folder=True,
                        **sorter_params)

sorter_log = f"tmp_{sorter_name}" / f"{sorter_name}.log"

# save sorting output in the cloud
sorting = sorting.save(folder=f"output/{sorter_name}_output")

# done spike sorting

####################################### OUTPUTS ###############################################
#
# - "output/{sorter_name}_output" 
# - "output/sorter_log"
#
##############################################################################################