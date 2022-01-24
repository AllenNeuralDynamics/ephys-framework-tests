from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean, Date

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
        return f'{self.specimen_id} {self.sex} {self.full_genotype} u={self.unit_count} cc={self.channel_count} pc={self.probe_count}'

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


    
                              
    
    
                   
                
            
    
