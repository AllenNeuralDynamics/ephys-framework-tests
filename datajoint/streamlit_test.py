import streamlit as st
import numpy as np
import pandas as pd
import datajoint as dj
from matplotlib import pyplot as plt

# Establish connection to the datajoint
dj.config['database.host'] = '34.82.94.188'
dj.config['database.user'] = 'yonib'
dj.config['database.password'] = 'yonib'
dj.conn()

schema  = dj.schema('yonib_behavior_test',locals())

# Load the schema
@schema 
class Genotype(dj.Lookup):
    definition = """
    genotype:varchar(255)
    """
    contents = zip(['Pvalb-IRES-Cre/wt;Ai32(RCL-ChR2(H134R)_EYFP)/wt',
       'Sst-IRES-Cre/wt;Ai32(RCL-ChR2(H134R)_EYFP)/wt',
       'Vip-IRES-Cre/wt;Ai32(RCL-ChR2(H134R)_EYFP)/wt', 'wt/wt'])

@schema
class SessionType(dj.Lookup):
    definition = """
    session_type:varchar(255)
    """
    contents = zip(['brain_observatory_1.1', 
                    'functional_connectivity'])


@schema
class Mouse(dj.Manual):
    definition = """
    # mouse information
    specimen_id: bigint  # unique mouse ID
    ---
    sex:enum('M','F','U') # Sex: Male, Female, Unkown
    -> Genotype
    dob:date
    """

# In my present formulation, things like channel and probe counts 
# and area ID can be found with queries but aren't included in the 
# Sessions table.
@schema
class Session(dj.Manual):
    definition = """
    session_id:bigint
    ---
    ->Mouse
    session_datetime:datetime
    ->SessionType
    publication_datetime:datetime
    """
@schema
class StimulusType(dj.Lookup):
    definition = """
    stimulus_name:varchar(255)
    """
    contents = zip(['drifting_gratings', 'flashes', 'gabors', 'invalid_presentation',
       'natural_movie_one', 'natural_movie_three', 'natural_scenes',
       'spontaneous', 'static_gratings']) 

@schema 
class Stimulus(dj.Manual):
    definition = """
    ->Session
    stimulus_presentation_id:int
    ---
    color=null:tinyblob
    contrast=null:float
    frame = null:int
    orientation = null:float
    phase = null:tinyblob
    size = null:tinyblob
    spatial_frequency = null:tinyblob
    start_time = null:float
    stimulus_block = null:int
    ->StimulusType
    stop_time = null:float
    temporal_frequency = null:tinyblob
    x_position = null:float
    y_position = null:float
    duration = null:float
    stimulus_condition_id = null:int
    """
@schema
class ProbePhase(dj.Lookup):
    definition = """
    probe_phase:varchar(255)
    """
    contents = zip(['3a', 'PXI'])
    
@schema 
class Probe(dj.Manual):
    definition = """
    probe_id:bigint
    ---
    ->Session
    ->ProbePhase
    probe_name:varchar(10)
    air_channel_index:int
    surface_channel_index:int
    sampling_rate:float
    lfp_sampling_rate:float

    """
@schema
class BrainStructure(dj.Lookup):
    definition = """
    brain_structure:varchar(10)
    """
    contents = zip(['APN', 'BMAa', 'CA1', 'CA2', 'CA3', 'COAa', 'COApm', 'CP', 'DG',
       'Eth', 'HPF', 'IGL', 'IntG', 'LD', 'LGd', 'LGv', 'LP', 'LT', 'MB',
       'MGd', 'MGm', 'MGv', 'MRN', 'NOT', 'OLF', 'OP', 'PF', 'PIL', 'PO',
       'POL', 'POST', 'PP', 'PPT', 'PRE', 'PoT', 'ProS', 'RPF', 'RT',
       'SCig', 'SCiw', 'SCop', 'SCsg', 'SCzo', 'SGN', 'SUB', 'TH', 'VIS',
       'VISal', 'VISam', 'VISl', 'VISli', 'VISmma', 'VISmmp', 'VISp',
       'VISpm', 'VISrl', 'VL', 'VPL', 'VPM', 'ZI', 'grey', 'nan'])
    
@schema
class Channel(dj.Manual):
    definition = """
    channel_id:bigint
    ---
    ->Probe
    ->BrainStructure
    structure_id = null:float
    local_channel_index:int
    probe_horizontal_position:int
    probe_vertical_position:int
    anterior_posterior_ccf_coordinate = null:float
    dorsal_ventral_ccf_coordinate = null:float
    left_right_ccf_coordinate=null:float
    """ 
@schema
class LFP(dj.Manual):
    definition = """
    ->Channel
    ---
    lfp_ts:longblob
    lfp:longblob
    """
    
@schema 
class Unit(dj.Manual):
    definition = """
    unit_id:bigint
    ---
    ->Channel
    pt_ratio = null:float
    amplitude = null:float
    amplitude_cutoff = null:float
    cumulative_drift = null:float
    d_prime = null:float
    duration = null:float
    firing_rate = null:float
    halfwidth = null:float
    isi_violations = null:float
    isolation_distance = null:float
    l_ratio = null:float
    max_drift = null:float
    nn_hit_rate = null:float
    nn_miss_rate = null:float
    presence_ratio = null:float
    recovery_slope = null:float
    repolarization_slope = null:float
    silhouette_score = null:float
    snr = null:float
    spread = null:float
    velocity_above = null:float
    velocity_below = null:float
    """
    
@schema
class SpikeTrain(dj.Manual):
    definition = """
    ->Unit
    ---
    spike_ts:longblob
    """
    

@schema
class Running(dj.Manual):
    definition= """
    ->Session
    ---
    running_ts=null:longblob
    velocity=null:longblob
    """

@schema
class Pupil(dj.Manual):
    definition= """
    ->Session
    ---
    pupil_ts:longblob
    pupil_size:longblob
    """
    
@schema
class Gaze(dj.Manual):
    definition= """
    ->Session
    ---
    gaze_ts:longblob
    gaze_position:longblob
    """

@schema
class SessionNWBFolder(dj.Manual):
    definition = """
    nwb_folder:varchar(256)
    """

# Set up the title
st.title('Test DataJoint Visualization')

sessions = Session().fetch(format = 'frame')
st.subheader('Probes Table')
session_option = st.selectbox('Session ID', sessions.index)
st.dataframe((Probe()&['session_id = '+str(session_option)]).fetch())

#
st.subheader('Channel Table')
probe_option = st.selectbox('Probe ID', (Probe()&['session_id = '+str(session_option)]).fetch('probe_id'))
st.dataframe((Channel()&['probe_id = '+str(probe_option)]).fetch())

#
st.subheader('Unit Table')
st.dataframe(Unit()&(Channel()&['probe_id = '+str(probe_option)]).fetch())

# Make a ISI histogram
unit_option = st.selectbox('Unit ID', (Unit()&(Channel()&['probe_id = '+str(probe_option)])).fetch('unit_id'))
spike_ts = (SpikeTrain()&['unit_id = '+str(unit_option)]).fetch1('spike_ts')
fig = plt.figure()
plt.hist(np.diff(spike_ts),np.arange(0,500)*.001)
plt.xlabel('Inter-Spike-Interval (sec)')
plt.ylabel('# of Spikes')
st.pyplot(fig)

