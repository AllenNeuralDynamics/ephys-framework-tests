from allensdk.brain_observatory.ecephys.ecephys_project_cache import EcephysProjectCache

import json
import numpy as np
import pandas as pd
from datetime import date,datetime,timedelta

from django_connect import connect
connect()

from db.models import *

def get_ecephys_cache():
    manifest = '/allen/scratch/aindtemp/david.feng/epc/manifest.json'
    return EcephysProjectCache(manifest=manifest)

def ingest_core():

    cache = get_ecephys_cache()

    sessions = cache.get_session_table(suppress=[])
    probes = cache.get_probes()
    channels = cache.get_channels()
    units = cache.get_units(filter_by_validity=False,
                            amplitude_cutoff_maximum = np.inf,
                            presence_ratio_minimum = -np.inf,
                            isi_violations_maximum = np.inf)


    # preprocess sessions
    sessions['acquisition_datetime'] = sessions['date_of_acquisition'].map(lambda v: datetime.strptime(v, "%Y-%m-%dT%H:%M:%S%z"))
    sessions['publication_datetime'] = sessions['published_at'].map(lambda v: datetime.strptime(v, "%Y-%m-%dT%H:%M:%S%z"))
    sessions.drop(columns=['date_of_acquisition',
                           'published_at'],
                  inplace=True)

    # ingest genotypes
    unique_genotypes = sessions['full_genotype'].unique()
    genotypes = pd.DataFrame(data={'name': unique_genotypes}).reset_index().rename(columns={'index':'id'})
    Genotype.objects.all().delete()
    Genotype.objects.bulk_create([ Genotype(**v) for v in genotypes.to_dict(orient='records') ])

    # ingest mice
    mice = sessions[['acquisition_datetime', 'age_in_days', 'specimen_id','sex','full_genotype']]
    mice['date_of_birth'] = mice.apply(lambda r: r['acquisition_datetime'].date() - timedelta(r['age_in_days']), axis=1)
    mice = mice[['specimen_id','sex','date_of_birth','full_genotype']].set_index('specimen_id')
    mice = mice.reset_index().merge(genotypes, left_on='full_genotype', right_on='name').rename(columns={'specimen_id':'id', 'id':'genotype_id'}).drop(columns=['full_genotype','name'])

    Mouse.objects.all().delete()
    Mouse.objects.bulk_create([ Mouse(**v) for v in mice.to_dict(orient='records') ])
 
    # ingest structures
    # http://api.brain-map.org/api/v2/data/Structure/query.json?include=[graph_id$eq1]&num_rows=2000
    with open('../pgaf/ccf_structures.json','r') as f:
        structures = json.load(f)
        structures = pd.DataFrame.from_records(structures['msg'])

    structures = structures[['acronym', 'name', 'color_hex_triplet', 'id', 'structure_id_path', 'hemisphere_id', 'graph_order', 'parent_structure_id']]
    structures.replace(np.nan, None, inplace=True)
    structures = structures.rename(columns={'acronym':'abbreviation'})

    Structure.objects.all().delete()
    Structure.objects.bulk_create([ Structure(**v) for v in structures.to_dict(orient='records') ])
    
    # ingest session_types
    session_types = pd.DataFrame(data={'name': sessions['session_type'].unique()}).reset_index().rename(columns={'index':'id'})

    SessionType.objects.all().delete()
    SessionType.objects.bulk_create([ SessionType(**v) for v in session_types.to_dict(orient='records') ])

    # ingest sessions
    sessions = sessions[['specimen_id','session_type','acquisition_datetime','publication_datetime']]
    sessions = sessions.reset_index().merge(session_types, left_on='session_type', right_on='name')
    sessions = sessions.rename(columns={'id_x':'id', 'id_y':'session_type_id'}).drop(columns=['session_type','name']) 

    Session.objects.all().delete()
    Session.objects.bulk_create([ Session(**v) for v in sessions.to_dict(orient='records') ])

    # ingest probe phases
    probe_phases = pd.DataFrame(data={'name': probes['phase'].unique()}).reset_index().rename(columns={'index':'id'})

    ProbePhase.objects.all().delete()
    ProbePhase.objects.bulk_create([ ProbePhase(**v) for v in probe_phases.to_dict(orient='records') ])

    # ingest probes
    probes = probes[['ecephys_session_id','phase','lfp_sampling_rate','sampling_rate','name']].rename(columns={'name':'probe_name'}).reset_index()
    probes = probes.merge(probe_phases, left_on='phase', right_on='name')
    probes = probes.rename(columns={'id_x':'id','id_y':'probe_phase_id','ecephys_session_id':'session_id'}).drop(columns=['phase','name'])

    SessionProbe.objects.all().delete()
    SessionProbe.objects.bulk_create([ SessionProbe(**v) for v in probes.to_dict(orient='records') ])

    # ingest channels
    channels = channels.reset_index().rename(columns={'ecephys_probe_id':'session_probe_id', 'ecephys_structure_id':'structure_id'})
    channels = channels.drop(columns=['unit_count','has_lfp_data','phase','ecephys_structure_acronym','ecephys_session_id'])
    channels['structure_id'].replace(np.nan, None, inplace=True)

    Channel.objects.all().delete()
    Channel.objects.bulk_create([ Channel(**v) for v in channels.to_dict(orient='records') ])

    # ingest units
    units = units.reset_index().rename(columns={'ecephys_channel_id':'channel_id','waveform_PT_ratio':'waveform_pt_ratio','L_ratio':'l_ratio'})
    units = units[['amplitude_cutoff', 'cumulative_drift', 'd_prime',
                   'firing_rate', 'isi_violations', 'isolation_distance',
                   'l_ratio', 'max_drift', 'nn_hit_rate', 'nn_miss_rate',
                   'presence_ratio', 'silhouette_score', 'snr', 'quality',
                   'waveform_pt_ratio', 'waveform_amplitude', 'waveform_duration',
                   'waveform_halfwidth', 'waveform_spread', 'waveform_velocity_above',
                   'waveform_velocity_below', 'waveform_recovery_slope',
                   'waveform_repolarization_slope', 'id', 'channel_id']]

    Unit.objects.all().delete()
    Unit.objects.bulk_create([ Unit(**v) for v in units.to_dict(orient='records') ])

if __name__ == "__main__": ingest_core()
