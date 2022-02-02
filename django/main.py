from django_connect import connect

connect()

from db.models import *
from django_pandas.io import read_frame

df = read_frame(Session.objects.filter(session_type__name = 'brain_observatory_1.1'))
print(df.head())
print(len(df))

""" prints:
          id                  specimen session_type acquisition_datetime publication_datetime
0  715093703  Mouse object (699733581)         None  2019-01-19 08:54:18           2019-10-03
1  719161530  Mouse object (703279284)         None  2019-01-09 00:25:16           2019-10-03
2  721123822  Mouse object (707296982)         None  2019-01-09 00:25:35           2019-10-03
3  732592105  Mouse object (717038288)         None  2019-01-09 00:26:20           2019-10-03
4  737581020  Mouse object (718643567)         None  2018-09-25 21:03:59           2019-10-03
32
"""

