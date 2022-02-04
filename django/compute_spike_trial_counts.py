from django_connect import connect
connect()

from django_pandas.io import read_frame

import os

import json
import numpy as np
import pandas as pd
from datetime import date,datetime,timedelta

import ingest
from db.models import *


def query_to_df(Q):
    df = pd.read_sql(Q.statement, Q.session.bind)
    return df

def spike_count(start_trigger,end_trigger,spike_ts):
    count = [None]*len(start_trigger)
    for ii,trigger in enumerate(start_trigger):
        count[ii] = np.sum(np.logical_and(spike_ts>=trigger,spike_ts<end_trigger[ii]))
    return count

def compute_trial_spike_counts(session):

    print('Session = ' + str(session))

    stim_table = StimulusPresentation.objects.filter(session=session)
    stim_table = read_frame(stim_table)

    if len(stim_table) == 0:
        return

    unit_table = Unit.objects.filter(channel__session_probe__session=session)

    duration = stim_table.stop_time-stim_table.start_time

    for unit in unit_table:
        spike_times = UnitSpikeTimes.objects.filter(unit=unit)

        if len(spike_times) == 0:
            continue

        spike_times = np.array(spike_times.first().spike_times)

        count = spike_count(stim_table.start_time,stim_table.stop_time,spike_times)
        this_df = pd.DataFrame(data = {
            'unit_id':int(unit.id),
            'stimulus_id':stim_table.id.values.astype(int),
            'spike_count':count,
            'spike_rate':np.divide(count,duration)
        })

        TrialSpikeCounts.objects.bulk_create([TrialSpikeCounts(**v) for v in this_df.to_dict(orient='records')])
        
def main():
    TrialSpikeCounts.objects.all().delete()

    sessions = Session.objects.all()

    for session in sessions:
        compute_trial_spike_counts(session)

if __name__ == '__main__': main()

