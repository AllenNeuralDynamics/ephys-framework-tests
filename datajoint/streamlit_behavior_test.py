import streamlit as st
import numpy as np
import pandas as pd
import datajoint as dj
from matplotlib import pyplot as plt

# Because streamlit doesn't seem to reload packages,
# This is just here while I debug some stuff

from importlib import reload
plt = reload(plt)

import yoni_behavior_schema
from yoni_behavior_schema import Session,Probe,Channel,Unit,SpikeTrain,TrialSpikeCount,Stimulus

# Set up the title
st.title('DataJoint Visualization')

sessions = Session().fetch(format = 'frame')
session_option = st.sidebar.selectbox('Session ID', sessions.index)

# Brain Area selector
brain_area_list = np.unique((Channel()&(Probe()&['session_id = '+str(session_option)])).fetch('brain_structure'))

brain_area_option = st.sidebar.selectbox('Brain Area', brain_area_list)

# Select the unit, get the spike train
unit_option = st.sidebar.selectbox('Unit ID', (Unit()&(Channel()&['brain_structure = "'+
brain_area_option +'"'])).fetch('unit_id'))

spike_ts = (SpikeTrain()&['unit_id = '+str(unit_option)]).fetch1('spike_ts')

# Make a ISI histogram
isi_container = st.container()

fig1 = plt.figure()
isi_container.subheader("ISI Distribution")
plt.hist(np.diff(spike_ts),np.arange(0,500)*.001)
plt.xlabel('Inter-Spike-Interval (sec)')
plt.ylabel('# of Spikes')
isi_container.pyplot(fig1)

# Set up container for receptive fields
rf_container = st.container()
rf_col,grating_col = rf_container.columns(2)
rf_col.subheader("Spatial Receptive Field")
grating_col.subheader("Grating Selectivity")


@st.cache
def compute_rf(unit_id):
    rf_df = ((TrialSpikeCount()&['unit_id = ' +str(unit_id)])*(Stimulus())&'stimulus_name = "gabors"').fetch(format = 'frame')
    C = rf_df[['x_position','y_position','spike_rate']].groupby(['x_position','y_position']).mean()
    x_vals = np.unique(C.index.get_level_values(0)).astype('float')
    y_vals = np.unique(C.index.get_level_values(1)).astype('float')
    return C,x_vals,y_vals


@st.cache
def compute_static_response(unit_id):
    static_frame = ((TrialSpikeCount()&['unit_id = ' +str(unit_id)])*(Stimulus())&'stimulus_name = "static_gratings"').fetch(format = 'frame')
    C = static_frame[['spatial_frequency','orientation','spike_rate']].groupby(['spatial_frequency','orientation']).mean()
    freq_vals= np.unique(C.index.get_level_values(0)).astype('float')
    orient_vals = np.unique(C.index.get_level_values(1)).astype('float')
    return C,freq_vals,orient_vals

@st.cache
def compute_drifting_response(unit_id):
    static_frame = ((TrialSpikeCount()&['unit_id = ' +str(unit_id)])*(Stimulus())&'stimulus_name = "drifting_gratings"').fetch(format = 'frame')
    C = static_frame[['temporal_frequency','orientation','spike_rate']].groupby(['temporal_frequency','orientation']).mean()
    freq_vals= np.unique(C.index.get_level_values(0)).astype('float')
    orient_vals = np.unique(C.index.get_level_values(1)).astype('float')
    return C,freq_vals,orient_vals

# Compute RF 
C,x_vals,y_vals = compute_rf(unit_option)

fig2 = plt.figure()
plt.pcolor(np.reshape(C.spike_rate.values,(len(x_vals),len(y_vals))))
plt.xticks(.5+np.arange(len(x_vals)),x_vals)
plt.yticks(.5+np.arange(len(y_vals)),y_vals)
plt.clim(0,np.max(C.spike_rate.values))
cbar = plt.colorbar()
cbar.set_label('Rate (hz)')
plt.xlabel('X position')
plt.ylabel('Y position')
rf_col.pyplot(fig2)

# Compute Static Grating Response
C,freq_vals,orient_vals = compute_static_response(unit_option)
fig3 = plt.figure()
plt.pcolor(np.reshape(C.spike_rate.values,(len(freq_vals),len(orient_vals))))
plt.xticks(.5+np.arange(len(orient_vals)),orient_vals)
plt.yticks(.5+np.arange(len(freq_vals)),freq_vals)
plt.clim(0,np.max(C.spike_rate.values))
cbar = plt.colorbar()
cbar.set_label('Rate (hz)')
plt.xlabel('Orientation (deg)')
plt.ylabel('Spatial Freq')
grating_col.pyplot(fig3)

# Compute Static Grating Response
C,freq_vals,orient_vals = compute_drifting_response(unit_option)
fig3 = plt.figure()
plt.pcolor(np.reshape(C.spike_rate.values,(len(freq_vals),len(orient_vals))))
plt.xticks(.5+np.arange(len(orient_vals)),orient_vals)
plt.yticks(.5+np.arange(len(freq_vals)),freq_vals)
plt.clim(0,np.max(C.spike_rate.values))
cbar = plt.colorbar()
cbar.set_label('Rate (hz)')
plt.xlabel('Orientation (deg)')
plt.ylabel('Temporal Freq')
grating_col.pyplot(fig3)










