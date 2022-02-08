import numpy as np
import numbers
import ast
from allensdk.brain_observatory.ecephys.ecephys_project_cache import EcephysProjectCache

def get_session(session_id):
    manifest = '/allen/scratch/aindtemp/david.feng/epc/manifest.json'
    cache =  EcephysProjectCache(manifest=manifest)
    return cache.get_session_data(session_id)

def spike_count(start_trigger,end_trigger,spike_ts):
    count = [None]*len(start_trigger)
    for ii,trigger in enumerate(start_trigger):
        count[ii] = np.sum(np.logical_and(spike_ts>=trigger,spike_ts<end_trigger[ii]))
    return count

def clean_string(v):
    if v is None:
        return None

    if isinstance(v, numbers.Number):
        return v

    v = ast.literal_eval(v.strip())

    if isinstance(v, list):
        return v[0]
    return v
