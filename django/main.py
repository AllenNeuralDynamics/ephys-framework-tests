from django_connect import connect

connect()

import numpy as np
from db.models import *
from django_pandas.io import read_frame
from django.db.models import Count
from django.contrib.postgres.aggregates import StringAgg

# query for sessions by session_type
qs = Session.objects.filter(session_type__name = 'brain_observatory_1.1')
df = read_frame(qs, index_col='id')
print(df.head())
print(len(df))

""" prints:
                           specimen session_type acquisition_datetime publication_datetime
id                                                                                        
715093703  Mouse object (699733581)         None  2019-01-19 08:54:18           2019-10-03
719161530  Mouse object (703279284)         None  2019-01-09 00:25:16           2019-10-03
721123822  Mouse object (707296982)         None  2019-01-09 00:25:35           2019-10-03
732592105  Mouse object (717038288)         None  2019-01-09 00:26:20           2019-10-03
737581020  Mouse object (718643567)         None  2018-09-25 21:03:59           2019-10-03
32
"""

# same, but resolve joins and just get columns of interest, also uses slice notation to limit to first five entries
qs = Session.objects.annotate(
    probe_count=Count('sessionprobe',distinct=True),
    structures=StringAgg('sessionprobe__channel__structure__abbreviation', distinct=True, delimiter=',')
)[:5].values(
    'id',
    'publication_datetime',
    'acquisition_datetime',
    'specimen__sex',
    'specimen__date_of_birth',
    'specimen__genotype__name',
    'session_type__name',
    'probe_count',
    'structures'
)
df = read_frame(qs, index_col='id')
print(df)

""" prints:
          publication_datetime acquisition_datetime specimen__sex  ...     session_type__name probe_count                                         structures
id                                                                 ...                                                                                      
715093703           2019-10-03  2019-01-19 08:54:18             M  ...  brain_observatory_1.1           6  APN,CA1,CA3,DG,grey,LGd,LP,MB,PO,PoT,VISam,VIS...
719161530           2019-10-03  2019-01-09 00:25:16             M  ...  brain_observatory_1.1           6  APN,CA1,CA2,CA3,DG,Eth,grey,LGd,LP,MB,NOT,PO,P...
721123822           2019-10-03  2019-01-09 00:25:35             M  ...  brain_observatory_1.1           6  APN,CA1,CA3,DG,HPF,LGd,LGv,LP,MB,NOT,POL,PPT,P...
732592105           2019-10-03  2019-01-09 00:26:20             M  ...  brain_observatory_1.1           5                   grey,VISal,VISl,VISp,VISpm,VISrl
737581020           2019-10-03  2018-09-25 21:03:59             M  ...  brain_observatory_1.1           6                  grey,VISl,VISmma,VISp,VISpm,VISrl

[5 rows x 8 columns]

"""

st = UnitSpikeTimes.objects.first()
print(np.array(st.spike_times))

""" prints
[6.21189230e-01 9.07956176e-01 1.08165635e+00 ... 9.81095051e+03
 9.81105404e+03 9.81113171e+03]

"""
