import spikeinterface as si
import spikeinterface.sorters as ss

# the capsule/image will determine which sorter to run 
# (because it will be the only one installed in the container)
sorter_name = "kilosort2_5"

# we might also use the parallel capabilities to do some parameter search
sorter_params = {}

preprocessed_folder = "somewhere_in_the_cloud"

# load the preprocessed folder from bucket/codocean output
recording_preprocessed = si.load_extractor(preprocessed_folder)

# run spike sorting 
# NOTE: we don't use the docker/singularity mechanism here because the sorter is installed "locally"
sorting = ss.run_sorter(sorter_name=sorter_params=, recording=recording_preprocessed,
                        output_folder="some_output", delete_output_folder=True,
                        **sorter_params)

# save sorting output in the cloud
sorting = sorting.save(folder=f"output/{sorter_name}_output")

# done spike sorting