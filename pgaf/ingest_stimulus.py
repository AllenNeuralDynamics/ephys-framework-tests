from allensdk.brain_observatory.ecephys.ecephys_project_cache import EcephysProjectCache
import os
from sqlalchemy import delete
from sqlalchemy.orm import sessionmaker

import json
import numpy as np
import pandas as pd
from datetime import date,datetime,timedelta

import sqla_schema as sch

import ingest

data_directory = 'C:\\Users\\yoni.browning\\Documents\\DataJoint\\AllenData'
manifest_path = os.path.join(data_directory, "manifest.json")

def get_first_value(value):
    if isinstance(value,str):
        if '[' in value and ']' in value:
            value = np.fromstring(value[1:-1],sep = ',')
            value = value[0]
        else:
            value = float(value)
    elif isinstance(value,np.ndarray) and len(value)==1:
        value = value[0]
    elif isinstance(value,int) or isinstance(value,float):
        value =value
    else:
        value = None
    return value

def query_to_df(Q):
    df = pd.read_sql(Q.statement, Q.session.bind)
    return df

def ingest_session_stimulus(session, engine):
    with sessionmaker(engine)() as dbsession:
        rf_stim_table = session.stimulus_presentations
        rf_stim_table.reset_index(inplace=True)
        rf_stim_table.insert(0,'session_id',\
                             (session.ecephys_session_id*np.ones(len(rf_stim_table))).\
                             astype(int))
        K = rf_stim_table.keys()
        # Fix 'null' to be None variables
        for ii in range(len(K)):
            rf_stim_table[K[ii]][rf_stim_table[K[ii]]=='null'] = None
        # Convert strings to arrays
        rf_stim_table['phase'] = rf_stim_table['phase'].apply(get_first_value)
        rf_stim_table['size'] = rf_stim_table['size'].apply(get_first_value)
        rf_stim_table['temporal_frequency'] =\
            rf_stim_table['temporal_frequency'].apply(get_first_value).astype(float)
        rf_stim_table['spatial_frequency'] = \
            rf_stim_table['spatial_frequency'].apply(get_first_value).astype(float)
        rf_stim_table.to_sql('stimulus', engine, index_label='id', if_exists='append')
        



def main():
    # Connect to the database (kinda worthless without this)
    engine = ingest.connect_to_db()
    print('Connected to engine')
    # Distroy any existing versions of these table
    #sch.Base.metadata.drop_all(engine, tables=(sch.StimulusType.__table__,))
    #sch.Base.metadata.drop_all(engine, tables=(sch.Stimulus.__table__,))
    print('Killed old tables')

    # Generate a new version of these tables
    sch.Base.metadata.create_all(engine, tables=(sch.StimulusType.__table__,))
    #sch.Base.metadata.create_all(engine, tables=(sch.Stimulus.__table__,))
    print('Spawned new tables')

    # 
    cache = ingest.get_ecephys_cache(manifest = manifest_path)
    
    # Add Stimulus Type arguments. 
    # This bit is a little funky, but you only need to do it once.
    session = cache.get_session_data(715093703)
    print('Grabbed some data')

    rf_stim_table = session.stimulus_presentations
    stimulus_name_df = \
        pd.DataFrame(data={'stimulus_name': rf_stim_table['stimulus_name'].unique()})
    stimulus_name_df.to_sql('stimulus_type', engine, index_label='id', if_exists='append')
    print('Added to DB')

    # loop through these sessions, get the data
    #ingest_session_stimulus(session, engine)
    # Actually do the ingest
    


# Run it!!!!
if __name__ == '__main__':main()
    
    
    