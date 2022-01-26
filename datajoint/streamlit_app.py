import streamlit as st
import datajoint as dj

# Establish connection
@st.cache
def connect():
	dj.config['database.host'] = '34.82.94.188'
	dj.config['database.user'] = 'yonib'
	dj.config['database.password'] = 'yonib'
	dj.conn()

connect()

import yoni_observatory_test

# configure a schema for testing stuff
st.title('Test Dashboard')

st.subheader('Sessions Table')

sessions = yoni_observatory_test.Session().fetch(format='frame')

option1 = st.selectbox('Session type', sessions.session_type.unique())

st.dataframe(sessions[sessions.session_type == option1])


st.subheader('Probes Table')

option2 = st.selectbox('Session ID', sessions[sessions.session_type == option1].index.values)

probes = yoni_observatory_test.Probe().fetch(format='frame')

st.dataframe(probes[probes.session_id == option2])
