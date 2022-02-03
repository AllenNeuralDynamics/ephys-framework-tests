from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean, Date
from sqlalchemy.types import ARRAY

Base = declarative_base()

class Mouse(Base):
    __tablename__ = 'mouse'
    
    id = Column(Integer, primary_key=True)
    sex = Column(String)
    date_of_birth = Column(Date)

    genotype_id = Column(Integer, ForeignKey('genotype.id'))

class Genotype(Base):
    __tablename__ = 'genotype'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Structure(Base):
    __tablename__ = 'structure'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    abbreviation = Column(String)
    color_hex_triplet = Column(String)
    structure_id_path = Column(String)
    hemisphere_id = Column(Integer)
    graph_order = Column(Integer)
    parent_structure_id = Column(Integer)

class SessionType(Base):
    __tablename__ = 'session_type'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
        
class Session(Base):
    __tablename__ = 'session'

    id = Column(Integer, primary_key=True)
    
    specimen_id = Column(Integer, ForeignKey('mouse.id'))
    session_type_id = Column(Integer, ForeignKey('session_type.id'))

    acquisition_datetime = Column(DateTime)
    publication_datetime = Column(DateTime)

    def __repr__(self):
        return f'{self.specimen_id} acquired: {self.acquisition_datetime} published: {self.publication_datetime}'

class ProbePhase(Base):
    __tablename__ = 'probe_phase'

    id = Column(Integer, primary_key=True)
    name = Column(String)

class SessionProbe(Base):
    __tablename__ = 'session_probe'

    id = Column(Integer, primary_key=True)    
    session_id = Column(Integer, ForeignKey('session.id'))
    probe_phase_id = Column(Integer, ForeignKey('probe_phase.id'))

    lfp_sampling_rate = Column(Float)
    sampling_rate = Column(Float)
    probe_name = Column(String)

class Channel(Base):
    __tablename__ = 'channel'
    
    id = Column(Integer, primary_key=True)

    session_probe_id = Column(Integer, ForeignKey('session_probe.id'))
    structure_id = Column(Integer, ForeignKey('structure.id'))
    
    local_index = Column(Integer)
    probe_horizontal_position = Column(Integer)
    probe_vertical_position = Column(Integer)
    anterior_posterior_ccf_coordinate = Column(Float)
    dorsal_ventral_ccf_coordinate = Column(Float)
    left_right_ccf_coordinate = Column(Float)

    lfp_sampling_rate = Column(Float)
    sampling_rate = Column(Float)

class UnitSpikeTimes(Base):
    __tablename__ = 'unit_spike_times'

    unit_id = Column(Integer, primary_key=True)
    spike_times = Column(ARRAY(Float))
    

class Unit(Base):
    __tablename__ = 'unit'

    id = Column(Integer, primary_key=True)

    channel_id = Column(Integer, ForeignKey('channel.id'))

    amplitude_cutoff = Column(Float)
    cumulative_drift = Column(Float)
    d_prime = Column(Float)
    firing_rate = Column(Float)
    isi_violations = Column(Integer)
    isolation_distance = Column(Float)
    L_ratio = Column(Float)
    max_drift = Column(Float)
    nn_hit_rate = Column(Float)
    nn_miss_rate = Column(Float)
    presence_ratio = Column(Float)
    silhouette_score = Column(Float)
    snr = Column(Float)
    quality = Column(String)
    waveform_PT_ratio = Column(Float)
    waveform_amplitude = Column(Float)
    waveform_duration = Column(Float)
    waveform_halfwidth = Column(Float)
    waveform_spread = Column(Float)
    waveform_velocity_above = Column(Float)
    waveform_velocity_below = Column(Float)
    waveform_recovery_slope = Column(Float)
    waveform_repolarization_slope = Column(Float)

class StimulusType(Base):
    __tablename__ = 'stimulus_type'

    id = Column(Integer, primary_key=True)
    name = Column(String)

class StimulusPresentation(Base):
    __tablename__ = 'stimulus_presentation'

    id = Column(Integer, primary_key=True, autoincrement=True)

    stimulus_type_id = Column(Integer, ForeignKey("stimulus_type.id"))
    session_id = Column(Integer, ForeignKey("session.id"))

    color = Column(Integer)
    contrast = Column(Float)
    frame = Column(Integer)
    orientation = Column(Integer)
    phase = Column(Float)
    size = Column(Float)
    spatial_frequency = Column(Float)
    stimulus_block = Column(Integer)
    start_time = Column(Float)
    stop_time = Column(Float)
    temporal_frequency = Column(Float)
    x_position = Column(Float)
    y_position = Column(Float)
    duration = Column(Float)
    stimulus_condition_id = Column(Integer)


class TrialSpikeCount(Base):
    __tablename__ = 'trial_spike_count'

    unit_id = Column(Integer, primary_key=True)
    
