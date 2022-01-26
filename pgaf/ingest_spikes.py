from allensdk.brain_observatory.ecephys.ecephys_project_cache import EcephysProjectCache

from sqlalchemy import delete
from sqlalchemy.orm import sessionmaker

import json
import numpy as np
import pandas as pd
from datetime import date,datetime,timedelta

import sqla_schema as sch

import ingest

def ingest_session_spikes(session, engine):
    with sessionmaker(engine)() as dbsession:
        for unit_id, unit_spike_times in session.spike_times.items():
            dbst = sch.UnitSpikeTimes(unit_id=unit_id, spike_times=unit_spike_times)
            print(unit_id)
            dbsession.add(dbst)
            dbsession.commit()

def main():

    engine = ingest.connect_to_db()
    sch.Base.metadata.drop_all(engine, tables=(sch.UnitSpikeTimes.__table__,))
    sch.Base.metadata.create_all(engine, tables=(sch.UnitSpikeTimes.__table__,))

    cache = ingest.get_ecephys_cache()

    sessions = cache.get_session_table(suppress=[])

    for idx,row in sessions.head(3).iterrows():
        session = cache.get_session_data(idx)
        ingest_session_spikes(session, engine)


if __name__ == '__main__': main()
