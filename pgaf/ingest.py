from allensdk.brain_observatory.ecephys.ecephys_project_cache import EcephysProjectCache

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

import sqla_schema as sch
import json


manifest = '/allen/scratch/aindtemp/david.feng/epc/manifest.json'
cache = EcephysProjectCache(manifest=manifest)

sessions = cache.get_session_table()
cache.get_probes()
cache.get_channels()
cache.get_units()

for idx,row in sessions.head(3).iterrows():
    cache.get_session_data(idx)

with open('SECRETS','r') as f:
    conn_info = json.load(f)

conn_string = f"postgresql://{conn_info['user']}:{conn_info['password']}@{conn_info['host']}:5432/{conn_info['dbname']}"

engine = create_engine(conn_string)
sch.Base.metadata.drop_all(engine)
sch.Base.metadata.create_all(engine)

sessions.drop(columns=['ecephys_structure_acronyms']).to_sql('session', engine, if_exists='append')

with Session(engine) as session:
    q = select(sch.Session).where(sch.Session.sex == 'M')
    for r in session.execute(q):
        print(r[0])
    

