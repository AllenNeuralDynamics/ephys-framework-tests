from allensdk.brain_observatory.ecephys.ecephys_project_cache import EcephysProjectCache
import os
from sqlalchemy import delete,insert
from sqlalchemy.orm import sessionmaker

import json
import numpy as np
import pandas as pd
from datetime import date,datetime,timedelta

from sqla_schema import *

import ingest

data_directory = 'C:\\Users\\yoni.browning\\Documents\\DataJoint\\AllenData'
manifest_path = os.path.join(data_directory, "manifest.json")

def query_to_df(Q):
    df = pd.read_sql(Q.statement, Q.session.bind)
    return df

def spike_count(start_trigger,end_trigger,spike_ts):
    count = [None]*len(start_trigger)
    for ii,trigger in enumerate(start_trigger):
        count[ii] = np.sum(np.logical_and(spike_ts>=trigger,spike_ts<end_trigger[ii]))
    return count

def compute_trial_spike_counts(engine,this_session):
    print('Session = ' + str(this_session))
    stim_table = query_to_df(S.query(Session.id.label('session_id'),\
            StimulusPresentation.id.label("stimulus_id"),\
            StimulusPresentation.stop_time,\
            StimulusPresentation.start_time).\
            join(StimulusPresentation).filter(Session.id==int(this_session)))

    unit_table =  query_to_df(S.query(Session.id.label('session_id'),\
            Unit.id.label("unit_id"),\
            UnitSpikeTimes.spike_times).join(SessionProbe).\
            join(Channel).join(Unit).join(UnitSpikeTimes,Unit.id==UnitSpikeTimes.unit_id).\
            filter(Session.id==int(this_session[0])))


    duration = stim_table.stop_time-stim_table.start_time

    for ii,row in unit_table.iterrows():
        print('Unit  = ' + str(row.unit_id) + ' is ' +  str(ii) + ' of ' + str(len(unit_table)) ) 
        count = spike_count(stim_table.start_time,stim_table.stop_time,np.array(row.spike_times))
        this_df = pd.DataFrame(data = \
                               {'unit_id':int(row.unit_id),\
                                'stimulus_id':np.array(stim_table.stimulus_id.values).astype(int),\
                                'spike_count':count,\
                                'spike_rate':np.divide(count,duration)})
        this_df.to_sql('trial_spike_count', engine,index = False, if_exists='append')
        
def main():
    engine = ingest.connect_to_db()
    S = sessionmaker(engine)()
    Base.metadata.drop_all(engine, tables=(TrialSpikeCount.__table__,))
    Base.metadata.create_all(engine, tables=(TrialSpikeCount.__table__,))

    for ii,this_session in enumerate(unique_sessions):
        compute_trial_spike_counts(engine,this_session[0])
        S.commit()

if __name__ == '__main__': main()

