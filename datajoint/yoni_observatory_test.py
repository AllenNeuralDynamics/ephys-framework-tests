import datajoint as dj
import pandas as pd

schema  = dj.schema('yonib_observatory_test',locals())

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
    has_nwb:bool
    isi_experiment_id:bigint
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
    local_index:int
    probe_horizontal_position:int
    probe_vertical_position:int
    anterior_posterior_ccf_coordinate = null:float
    dorsal_ventral_ccf_coordinate = null:float
    left_right_ccf_coordinate=null:float
    """

@schema
class Unit(dj.Manual):
    definition = """
    unit_id:bigint
    ---
    ->Channel
    pt_ration = null:float
    amplitude = null:float
    amplitude_cutoff = null:float
    cumulative_drift = null:float
    d_prime = null:float
    duration = null:float
    firing_rate = null:float
    halfwidth = null:float
    isi_violations = null:float
    isolation_distance = null:float
    l_ration = null:float
    max_drift = null:float
    nn_hit_rate = null:float
    nn_miss_rate = null:float
    presence_ration = null:float
    quality = null:varchar(10)
    recovery_slope = null:float
    repolarization_slope = null:float
    silhouette_score = null:float
    snr = null:float
    spread = null:float
    velocity_above = null:float
    velocity_below = null:float
    """

# I would prefer to have spiketrain data be part of the unit,
# But this is going to make more sense if we don't load all NWB files
@schema
class SpikeTrain(dj.Manual):
    definition = """
    ->Unit
    ---
    spike_ts:longblob
    """

@schema
class LFP(dj.Manual):
    definition = """
    ->Channel
    ---
    lfp_sampling_rate:float
    lfp:longblob
    """


# This notation is borrowed from the mesoscale folks.
# I am assuming that it is best practices?

@schema
class SessionCSV(dj.Manual):
    definition = """
    session_csv:varchar(255)
    """

@schema
class SessionIngest(dj.Imported):
    definition = """
    ->SessionCSV
    """

    def make(self,key):
        # For now, there is only one session file.
        self.insert1({'session_csv':
                      key['session_csv']},skip_duplicates = True)

        #
        df=pd.read_csv(key['session_csv'],index_col = 'id')
        for session_id,row in df.iterrows():
            session_datetime = datetime.strptime(row['date_of_acquisition'], "%Y-%m-%dT%H:%M:%S%z")
            publication_datetime = datetime.strptime(row['published_at'], "%Y-%m-%dT%H:%M:%S%z")

            specimen_id = row['specimen_id']
            # Add the mouse data
            mouse_data = {'specimen_id':row['specimen_id'],
                         'sex':row['sex'],
                         'genotype':row['genotype'],
                         'dob':session_datetime.date()-timedelta(row['age_in_days'])}
            Mouse().insert1(mouse_data,skip_duplicates = True)
            # Add the Session data
            session_data = {'session_id':session_id,
                            'specimen_id':row['specimen_id'],
                            'session_datetime':session_datetime,
                            'publication_datetime':publication_datetime,
                            'session_type':row['session_type'],
                            'has_nwb':row['has_nwb'],
                            'isi_experiment_id':row['isi_experiment_id'],
            }
            Session().insert1(session_data,skip_duplicates = True)


@schema
class ProbeCSV(dj.Manual):
    definition = """
    probe_csv:varchar(255)
    """

@schema
class ProbeIngest(dj.Imported):
    definition = """
    ->ProbeCSV
    """

    def make(self,key):
        self.insert1({'probe_csv':
              key['probe_csv']},skip_duplicates = True)

         #
        df=pd.read_csv(key['probe_csv'],index_col = 'id')
        for probe_id,row in df.iterrows():
            # Add the probe
            probe_data = {'probe_id':probe_id,
                            'session_id':row['ecephys_session_id'],
                            'probe_phase':row['phase'],
                            'probe_name':row['name'],
                            'air_channel_index':row['air_channel_index'],
                            'surface_channel_index':row['surface_channel_index'],
                            'sampling_rate':row['sampling_rate'],
                            'lfp_sampling_rate':row['lfp_sampling_rate']}

            Probe().insert1(probe_data,skip_duplicates = True)



@schema
class ChannelCSV(dj.Manual):
    definition = """
    channel_csv:varchar(255)
    """

# Note the difference in the insert commands between this Channel code and the code above.
# Before, tables were small enough form repeat insert calls.
# Here, we needed to brake things down to a single call.
# This switches it from takeing "so long yoni stopped waiting " to ~20 seconds to run.

@schema
class ChannelIngest(dj.Imported):
    definition = """
    ->ChannelCSV
    """

    def make(self,key):
        self.insert1({'channel_csv':
              key['channel_csv']},skip_duplicates = True)

        df=pd.read_csv(key['channel_csv'],index_col = 'id')
        channel_data_array = []
        for channel_id,row in df.iterrows():
            channel_data = {'channel_id':channel_id,
                            'probe_id':row['ecephys_probe_id'],
                            'brain_structure':str(row['ecephys_structure_acronym']),
                            'local_index':row['local_index'],
                            'probe_horizontal_position':row['probe_horizontal_position'],
                            'probe_vertical_position':row['probe_vertical_position'],
                            'anterior_posterior_ccf_coordinate':row['anterior_posterior_ccf_coordinate'],
                            'dorsal_ventral_ccf_coordinate':row['dorsal_ventral_ccf_coordinate'],
                            'left_right_ccf_coordinate':row['left_right_ccf_coordinate'],
                            'structure_id':row['ecephys_structure_id']}
            channel_data_array.append(channel_data)
        Channel().insert(tuple(channel_data_array))


@schema
class UnitCSV(dj.Manual):
    definition = """
    unit_csv:varchar(255)
    """

# This one was even weirder...I kept having a lost connection problem, so I set it to send every 1000 units

@schema
class UnitIngest(dj.Imported):
    definition = """
    ->UnitCSV
    """

    def make(self,key):
        self.insert1({'unit_csv':
              key['unit_csv']},skip_duplicates = True)

        df=pd.read_csv(key['unit_csv'],index_col = 'id')
        unit_data_array = []
        idx = 0
        for unit_id,row in df.iterrows():

            unit_data = {'unit_id':unit_id,
                            'channel_id':row['ecephys_channel_id'],
                            'pt_ration':row['PT_ratio'],
                            'amplitude':row['amplitude'],
                            'amplitude_cutoff':row['amplitude_cutoff'],
                            'cumulative_drift':row['cumulative_drift'],
                            'd_prime':row['d_prime'],
                            'duration':row['duration'],
                            'firing_rate':row['firing_rate'],
                            'halfwidth':row['halfwidth'],
                            'isi_violations':row['isi_violations'],
                            'isolation_distance':row['isolation_distance'],
                            'l_ration':row['l_ratio'],
                            'max_drift':row['max_drift'],
                            'nn_hit_rate':row['nn_hit_rate'],
                            'nn_miss_rate':row['nn_miss_rate'],
                            'presence_ration':row['presence_ratio'],
                            'quality':row['quality'],
                            'recovery_slope':row['recovery_slope'],
                            'repolarization_slope':row['repolarization_slope'],
                            'silhouette_score':row['silhouette_score'],
                            'snr':row['snr'],
                            'spread':row['spread'],
                            'velocity_above':row['velocity_above'],
                            'velocity_below':row['velocity_below'],}
            unit_data_array.append(unit_data)
            idx+=1
            if (idx%1000)==0:
                Unit().insert(tuple(unit_data_array))
                unit_data_array = []
                #print(idx)
        # gets anything that wasn't checkpointed
        Unit().insert(tuple(unit_data_array))