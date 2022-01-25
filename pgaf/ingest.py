from allensdk.brain_observatory.ecephys.ecephys_project_cache import EcephysProjectCache

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy_schemadisplay import create_schema_graph

import json
import numpy as np
import pandas as pd
from datetime import date,datetime,timedelta

import sqla_schema as sch

manifest = '/allen/scratch/aindtemp/david.feng/epc/manifest.json'
cache = EcephysProjectCache(manifest=manifest)

sessions = cache.get_session_table(suppress=[])
probes = cache.get_probes()
channels = cache.get_channels()
units = cache.get_units(filter_by_validity=False,
                        amplitude_cutoff_maximum = np.inf,
                        presence_ratio_minimum = -np.inf,
                        isi_violations_maximum = np.inf)

for idx,row in sessions.head(3).iterrows():
    cache.get_session_data(idx)

with open('SECRETS','r') as f:
    conn_info = json.load(f)

conn_string = f"postgresql://{conn_info['user']}:{conn_info['password']}@{conn_info['host']}:5432/{conn_info['dbname']}"

engine = create_engine(conn_string)
sch.Base.metadata.drop_all(engine)
sch.Base.metadata.create_all(engine)

graph = create_schema_graph(metadata=sch.Base.metadata,
                            show_datatypes=False,
                            show_indexes=False,
                            rankdir='LR',
                            concentrate=True)
graph.write_png('dbschema.png')


# preprocess sessions
sessions['acquisition_datetime'] = sessions['date_of_acquisition'].map(lambda v: datetime.strptime(v, "%Y-%m-%dT%H:%M:%S%z"))
sessions['publication_datetime'] = sessions['published_at'].map(lambda v: datetime.strptime(v, "%Y-%m-%dT%H:%M:%S%z"))
sessions.drop(columns=['date_of_acquisition',
                       'published_at'],
              inplace=True)

# ingest genotypes
genotypes = pd.DataFrame(data={'name': sessions['full_genotype'].unique()})
genotypes.to_sql('genotype', engine, index_label='id', if_exists='append')

# ingest mice
mice = sessions[['acquisition_datetime', 'age_in_days', 'specimen_id','sex','full_genotype']]
mice['date_of_birth'] = mice.apply(lambda r: r['acquisition_datetime'].date() - timedelta(r['age_in_days']), axis=1)
mice = mice.merge(genotypes.reset_index(), left_on='full_genotype', right_on='name', how='left').rename(columns={'index':'genotype_id'})
mice = mice[['specimen_id','sex','date_of_birth','genotype_id']].set_index('specimen_id')
mice.index.name ='id'
mice.to_sql('mouse', engine, index_label='id', if_exists='append')

# ingest structures
# http://api.brain-map.org/api/v2/data/Structure/query.json?include=[graph_id$eq1]&num_rows=2000
with open('ccf_structures.json','r') as f:
    structures = json.load(f)
    structures = pd.DataFrame.from_records(structures['msg'])

structures = structures[['acronym', 'name', 'color_hex_triplet', 'id', 'structure_id_path', 'hemisphere_id', 'graph_order', 'parent_structure_id']]
structures = structures.rename(columns={'acronym':'abbreviation'}).set_index('id')
structures.to_sql('structure', engine, index_label='id', if_exists='append')

# ingest session_types
session_types = pd.DataFrame(data={'name': sessions['session_type'].unique()})
session_types.to_sql('session_type', engine, index_label='id', if_exists='append')

# ingest sessions
sessions.drop(columns=['ecephys_structure_acronyms', 
                       'has_nwb', 
                       'isi_experiment_id', 
                       'age_in_days', 
                       'sex', 
                       'unit_count',
                       'channel_count', 
                       'probe_count'], 
              inplace=True)
sessions = sessions.reset_index().merge(session_types.reset_index(), left_on='session_type', right_on='name', how='left')
sessions = sessions[['id','specimen_id','acquisition_datetime','publication_datetime','index']].rename(columns={'index':'session_type_id'})
sessions = sessions.set_index('id')
sessions.to_sql('session', engine, if_exists='append')

# ingest probe phases
probe_phases = pd.DataFrame(data={'name': probes['phase'].unique()})
probe_phases.to_sql('probe_phase', engine, index_label='id', if_exists='append')

# ingest probes
probes = probes.reset_index().merge(probe_phases.reset_index(), left_on='phase', right_on='name', how='left')
probes = probes[['id','ecephys_session_id','lfp_sampling_rate','name_x','sampling_rate','index']].rename(columns={'name_x':'probe_name','index':'probe_phase_id','ecephys_session_id':'session_id'})
probes = probes.set_index('id')
probes.to_sql('session_probe', engine, if_exists='append')

# ingest channels
channels = channels.rename(columns={'ecephys_probe_id':'session_probe_id','ecephys_structure_id':'structure_id'})
channels = channels.drop(columns=['phase','ecephys_structure_acronym','unit_count','has_lfp_data','ecephys_session_id'])
channels.to_sql('channel', engine, index_label='id', if_exists='append')

# ingest units
units = units.rename(columns={'ecephys_channel_id':'channel_id'})
units = units.drop(columns=['ecephys_probe_id', 'local_index', 'probe_horizontal_position', 'probe_vertical_position',
                            'anterior_posterior_ccf_coordinate', 'dorsal_ventral_ccf_coordinate',
                            'left_right_ccf_coordinate', 'ecephys_structure_id',
                            'ecephys_structure_acronym', 'ecephys_session_id', 'lfp_sampling_rate',
                            'name', 'phase', 'sampling_rate', 'has_lfp_data', 'date_of_acquisition',
                            'published_at', 'specimen_id', 'session_type', 'age_in_days', 'sex',
                            'genotype'])
units.to_sql('unit', engine, index_label='id', if_exists='append')
