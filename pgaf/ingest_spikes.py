from allensdk.brain_observatory.ecephys.ecephys_project_cache import EcephysProjectCache

from sqlalchemy import delete
from sqlalchemy.orm import sessionmaker

import json
import numpy as np
import pandas as pd
from datetime import date,datetime,timedelta
import ast

import sqla_schema as sch

import ingest

def clean_string(v):
    if v is None:
        return None
    v = ast.literal_eval(v.strip())
    if isinstance(v, list):
        return v[0]
    return v

def ingest_stimulus_types(sessions, engine):
    stim_table = pd.concat([s.stimulus_presentations for s in sessions])
    
    # stimulus types
    stim_types = pd.DataFrame(data={'name': stim_table['stimulus_name'].unique()})
    stim_types.to_sql('stimulus_type', engine, index_label='id', if_exists='append')

def ingest_stimulus_presentations(session, engine):
    # stimulus types
    stim_types = pd.read_sql('stimulus_type', engine, index_col='id')
        
    # stimulus presentations
    stim_table = session.stimulus_presentations
    stim_table = stim_table.replace({'null':None})

    for k in ['phase','size','spatial_frequency']:
        stim_table[k] = stim_table[k].apply(clean_string)
            
    stim_table = stim_table.merge(stim_types.reset_index(), left_on='stimulus_name', right_on='name', how='left').rename(columns={'id':'stimulus_type_id'}).drop(columns=['stimulus_name','name'])
    stim_table['session_id'] = pd.Series([session.ecephys_session_id]*len(stim_table))
    stim_table.to_sql('stimulus_presentation', engine, index=False, if_exists='append')


def ingest_spike_times(session, engine):
    with sessionmaker(engine)() as dbsession:
        # spike times
        for unit_id, unit_spike_times in session.spike_times.items():
            dbst = sch.UnitSpikeTimes(unit_id=unit_id, spike_times=unit_spike_times)
            print(unit_id)
            dbsession.add(dbst)
            dbsession.commit()

def main():

    engine = ingest.connect_to_db()
    print("cleaning tables")
    tables = (sch.UnitSpikeTimes.__table__, sch.StimulusType.__table__, sch.StimulusPresentation.__table__)
    sch.Base.metadata.drop_all(engine, tables=tables)
    sch.Base.metadata.create_all(engine, tables=tables)

    cache = ingest.get_ecephys_cache()

    print("loading session metadata")
    sessions = cache.get_session_table(suppress=[]).head(3)

    all_session_data = [ cache.get_session_data(idx) for idx, row in sessions.iterrows() ]

    print("ingesting stimulus types")
    ingest_stimulus_types(all_session_data, engine)

    for session in all_session_data:
        print("ingesting stim table")
        ingest_stimulus_presentations(session, engine)

        print("ingesting spike times")
        ingest_spike_times(session, engine)


if __name__ == '__main__': main()
