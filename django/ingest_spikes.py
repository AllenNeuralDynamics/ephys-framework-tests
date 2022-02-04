from allensdk.brain_observatory.ecephys.ecephys_project_cache import EcephysProjectCache
import ingest

import json
import numpy as np
import pandas as pd
from datetime import date,datetime,timedelta
import ast

import numbers

from db.models import *
from django_pandas.io import read_frame


def clean_string(v):
    if v is None:
        return None

    if isinstance(v, numbers.Number):
        return v

    v = ast.literal_eval(v.strip())

    if isinstance(v, list):
        return v[0]
    return v

def ingest_stimulus_types(sessions):
    stim_table = pd.concat([s.stimulus_presentations for s in sessions])
    
    # stimulus types
    stim_types = pd.DataFrame(data={'name': stim_table['stimulus_name'].unique()}).reset_index().rename(columns={'index':'id'})
    StimulusType.objects.bulk_create([StimulusType(**v) for v in stim_types.to_dict(orient='records')])

def ingest_stimulus_presentations(session):
    # stimulus types
    stim_types = read_frame(StimulusType.objects.all())

    # stimulus presentations
    stim_table = session.stimulus_presentations
    stim_table = stim_table.replace({'null':None})

    for k in ['phase','size','spatial_frequency']:
        stim_table[k] = stim_table[k].apply(clean_string)

    stim_table = stim_table.reset_index()
    stim_table = stim_table.merge(stim_types.reset_index(), left_on='stimulus_name', right_on='name', how='left')
    stim_table = stim_table.rename(columns={'id':'stimulus_type_id','stimulus_presentation_id':'id'}).drop(columns=['stimulus_name','name','index'])
    stim_table['session_id'] = pd.Series([session.ecephys_session_id]*len(stim_table))
    stim_table = stim_table.fillna(np.nan).replace({np.nan:None})

    StimulusPresentation.objects.bulk_create([ StimulusPresentation(**v) for v in stim_table.to_dict(orient='records')])


def ingest_spike_times(session):
    # spike times
    for unit_id, unit_spike_times in session.spike_times.items():
        st = UnitSpikeTimes(unit_id=unit_id, spike_times=list(unit_spike_times))
        st.save()
        print(unit_id)


def main():

    print("cleaning tables")
    StimulusType.objects.all().delete()
    UnitSpikeTimes.objects.all().delete()
    StimulusPresentation.objects.all().delete()

    cache = ingest.get_ecephys_cache()

    print("loading session metadata")
    sessions = cache.get_session_table(suppress=[]).head(3)

    all_session_data = [ cache.get_session_data(idx) for idx, row in sessions.iterrows() ]

    print("ingesting stimulus types")
    ingest_stimulus_types(all_session_data)

    for session in all_session_data:
        print("ingesting stim table")
        ingest_stimulus_presentations(session)

        print("ingesting spike times")
        ingest_spike_times(session)


if __name__ == '__main__': main()
