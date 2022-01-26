import streamlit as st
from ingest import connect_to_db
import sqla_schema as schema
from sqlalchemy.orm import sessionmaker
import pandas as pd

# Establish connection
engine = connect_to_db()
session = sessionmaker(engine)()

# configure a schema for testing stuff
st.title('Test Dashboard')

st.subheader('Sessions Table')

q = session.query(schema.Session)
sessions = pd.read_sql(q.statement, q.session.bind)
print(sessions.head())

option1 = st.selectbox('Session type', sessions.session_type_id.unique())

st.dataframe(sessions[sessions.session_type_id == option1])


st.subheader('Probes Table')

option2 = st.selectbox('Session ID', sessions[sessions.session_type_id == option1].id)

q = session.query(schema.SessionProbe)
probes = pd.read_sql(q.statement, q.session.bind)
print(probes.head())

st.dataframe(probes[probes.session_id == option2])
