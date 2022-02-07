import streamlit as st
import numpy as np
import pandas as pd
import datajoint as dj
from matplotlib import pyplot as plt


from allensdk.brain_observatory.ecephys.ecephys_project_cache import EcephysProjectCache
import os
from sqlalchemy import delete,insert
from sqlalchemy.orm import sessionmaker

# Because streamlit doesn't seem to reload packages,
# This is just here while I debug some stuff

from importlib import reload
plt = reload(plt)


import ingest

from sqla_schema import *

engine = ingest.connect_to_db()
S = sessionmaker(engine)()


def query_to_df(Q):
    df = pd.read_sql(Q.statement, Q.session.bind)
    return df


# Set up the title
st.title('DataJoint Visualization')

sessions = query_to_df(S.query(Session.id).\
            join(SessionProbe).\
            join(Channel).\
            join(Unit).\
            join(UnitSpikeTimes,Unit.id==UnitSpikeTimes.unit_id).group_by(Session.id))
session_option = st.sidebar.selectbox('Session ID', sessions.id)

# Brain Area selector
brain_area_df = query_to_df(S.query(Session.id,Structure.name).\
                              join(SessionProbe).\
                              join(Channel).\
                              join(Structure).\
                              filter(Session.id==session_option).\
                              group_by(Session.id,Structure.name))

brain_area_option = st.sidebar.selectbox('Brain Area', brain_area_df.name)

# Select the unit, get the spike train

unit_df = query_to_df(S.query(Session.id,UnitSpikeTimes.unit_id).\
                join(SessionProbe).\
                join(Channel).\
                join(Structure).\
                join(Unit).\
                join(UnitSpikeTimes,Unit.id==UnitSpikeTimes.unit_id).\
                        filter(Session.id==session_option).\
                        filter(Structure.name == brain_area_option))

unit_option = st.sidebar.selectbox('Unit ID', unit_df.unit_id)


# 
spike_ts = S.query(UnitSpikeTimes.spike_times).\
       filter(UnitSpikeTimes.unit_id==unit_option).first()[0]


# Make a ISI histogram
isi_container = st.container()

fig1 = plt.figure()
isi_container.subheader("ISI Distribution")
plt.hist(np.diff(spike_ts),np.arange(0,500)*.001)
plt.xlabel('Inter-Spike-Interval (sec)')
plt.ylabel('# of Spikes')
isi_container.pyplot(fig1)

"""
# RF
static_contains = st.container()
fig2 = plt.figure()
static_contains.subheader("Static Gratings")

data = query_to_df(S.query(TrialSpikeCount.spike_rate,\
        StimulusPresentation.orientation,\
        StimulusPresentation.spatial_frequency).\
        join(StimulusPresentation).join(StimulusType).\
        filter(TrialSpikeCount.unit_id == 950907205).
        filter(StimulusType.name=='static_gratings'));
data = data.groupby(['spatial_frequency','orientation']).mean()

spatial_freq = np.unique(data.index.get_level_values(0))
orient = np.unique(data.index.get_level_values(1));

plt.pcolor(np.reshape(data.spike_rate.values,(len(spatial_freq),len(orient))))
plt.xticks(.5+np.arange(len(orient)),orient)
plt.yticks(.5+np.arange(len(spatial_freq)),spatial_freq)
plt.clim(0,np.max(data.spike_rate.values))
cbar = plt.colorbar()
cbar.set_label('Rate (hz)')
plt.xlabel('Orientation (deg)')
plt.ylabel('Spatial Freq')
static_contains.pyplot(fig2)


drifting_contains = st.container()
fig3 = plt.figure()
drifting_contains.subheader("Drifting Gratings")

data = query_to_df(S.query(TrialSpikeCount.spike_rate,\
        StimulusPresentation.orientation,\
        StimulusPresentation.temporal_frequency).\
        join(StimulusPresentation).join(StimulusType).\
        filter(TrialSpikeCount.unit_id == 950907205).
        filter(StimulusType.name=='drifting_gratings'));
data = data.groupby(['temporal_frequency','orientation']).mean()

time_freq = np.unique(data.index.get_level_values(0))
orient = np.unique(data.index.get_level_values(1));

plt.pcolor(np.reshape(data.spike_rate.values,(len(time_freq),len(orient))))
plt.xticks(.5+np.arange(len(orient)),orient)
plt.yticks(.5+np.arange(len(time_freq)),time_freq)
plt.clim(0,np.max(data.spike_rate.values))
cbar = plt.colorbar()
cbar.set_label('Rate (hz)')
plt.xlabel('Orientation (deg)')
plt.ylabel('Temp. Freq')
drifting_contains.pyplot(fig2)
"""

'''
# This version would get us only the units with Trial Spike Counts computed...kinda makes the app useless without data so commented out.

unit_df = query_to_df(S.query(Session.id,TrialSpikeCount.unit_id).\
                join(SessionProbe).\
                join(Channel).\
                join(Structure).\
                join(Unit).\
                join(TrialSpikeCount,Unit.id==TrialSpikeCount.unit_id).\
                        filter(Session.id==session_option).\
                        filter(Structure.name == brain_area_option))
'''










