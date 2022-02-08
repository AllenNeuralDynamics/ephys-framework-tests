import os
os.environ['PREFECT__LOGGING__LEVEL'] = 'DEBUG'
os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'

from prefect import flow, task

import numpy as np
import pandas as pd
from django_pandas.io import read_frame
import helpers

@task 
def insert_session(session_id):
    from django_connect import connect
    connect()
    import db.models as d

    session = helpers.get_session(session_id)

    d.StimulusPresentation.objects.filter(session_id=session_id).delete()

    # stimulus types
    stim_types = read_frame(d.StimulusType.objects.all())

    # stimulus presentations
    stim_table = session.stimulus_presentations
    stim_table = stim_table.replace({'null':None})

    for k in ['phase','size','spatial_frequency']:
        stim_table[k] = stim_table[k].apply(helpers.clean_string)

    stim_table = stim_table.reset_index()
    stim_table = stim_table.merge(stim_types.reset_index(), left_on='stimulus_name', right_on='name', how='left')
    stim_table = stim_table.rename(columns={'id':'stimulus_type_id'}).drop(columns=['stimulus_name','name','index'])
    stim_table['session_id'] = pd.Series([session.ecephys_session_id]*len(stim_table))
    stim_table = stim_table.fillna(np.nan).replace({np.nan:None})

    d.StimulusPresentation.objects.bulk_create([ d.StimulusPresentation(**v) for v in stim_table.to_dict(orient='records')])

@task
def list_units(session_id):
    from django_connect import connect
    connect()
    import db.models as d

    units = d.Unit.objects.filter(channel__session_probe__session_id=session_id)
    return [ int(u.id) for u in units ]


@task 
def insert_spike_times(session_id, unit_id):
    from django_connect import connect
    connect()
    import db.models as d

    print(f"insert_spike_times: session {session_id}, unit {unit_id}")
    st = d.UnitSpikeTimes.objects.filter(unit_id=unit_id).delete()

    session = helpers.get_session(session_id)

    if unit_id in session.spike_times:
        unit_spike_times = session.spike_times[unit_id]
        st = d.UnitSpikeTimes(unit_id=unit_id, spike_times=list(unit_spike_times))
        st.save()

@task 
def insert_trial_spike_counts(unit_id):
    from django_connect import connect
    connect()
    import db.models as d

    d.TrialSpikeCounts.objects.filter(unit_id=unit_id).delete()

    unit = d.Unit.objects.get(pk=unit_id)
    session = unit.channel.session_probe.session
    stim_table = d.StimulusPresentation.objects.filter(session=session)
    stim_table = read_frame(stim_table)

    unit_table = d.Unit.objects.filter(channel__session_probe__session=session)

    duration = stim_table.stop_time-stim_table.start_time

    spike_times = d.UnitSpikeTimes.objects.filter(unit=unit)

    if len(spike_times) == 0:
        return

    spike_times = np.array(spike_times.first().spike_times)

    count = helpers.spike_count(stim_table.start_time,stim_table.stop_time,spike_times)
    this_df = pd.DataFrame(data = {
        'unit_id':int(unit.id),
        'stimulus_id':stim_table.id.values.astype(int),
        'spike_count':count,
        'spike_rate':np.divide(count,duration)
    })

    d.TrialSpikeCounts.objects.bulk_create([d.TrialSpikeCounts(**v) for v in this_df.to_dict(orient='records')])

@flow(name="spikes")
def spike_flow(session_id):
    r0 = insert_session(session_id)
    unit_ids = list_units(session_id, wait_for=[r0])
    
    for unit_id in unit_ids.wait().result():
        r1 = insert_spike_times(session_id=session_id, unit_id=unit_id)
        insert_trial_spike_counts(unit_id=unit_id, wait_for=[r1])

if __name__ == "__main__": 
    spike_flow(session_id=732592105)
        
        

