import airflow
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import timedelta

import datajoint as dj
import pandas as pd

# Establish connection
dj.config['database.host'] = '34.82.94.188'
dj.config['database.user'] = 'yonib'
dj.config['database.password'] = 'yonib'
dj.conn()

# configure a schema for testing stuff
schema = dj.schema('yonib_test', locals())


# Set up a stupid schema, just to test out some basic stuff.
@schema
class StupidSimple(dj.Manual):
    definition = """
    x:float
    ---
    y:float
    """


@schema
class SquareX(dj.Imported):
    definition = """
    -> StupidSimple
    ---
    z:float
    """

    def _make_tuples(self, key):
        key['z'] = key['x']**2
        self.insert1(key)


@schema
class CubeY(dj.Computed):
    definition = """
    ->StupidSimple
    ---
    z:float
    """

    def _make_tuples(self, key):
        y = (StupidSimple() &key).fetch1('y')
        key['z'] = y**3
        self.insert1(key)


dag = DAG('airflow_insert_rows',
          description='Insert rows into a table, and populate downstream tables',
          schedule_interval=timedelta(minutes=60),
          dagrun_timeout=timedelta(minutes=60))


def _insert_row():
    stupid_simple = StupidSimple()

    last_key = stupid_simple.fetch()[-1][0]
    next_key = last_key + 1

    stupid_simple.insert1({'x': next_key, 'y': next_key * 0.1})


def _populate_SquareX():
    SquareX.populate()


def _populate_CubeY():
    CubeY.populate()


t1 = PythonOperator(
	task_id="insert_row",
	python_callable=_insert_row,
	dag=dag
	)

t2 = PythonOperator(
	task_id="populate_SquareX",
	python_callable=_populate_SquareX,
	dag=dag
	)

t2 = PythonOperator(
	task_id="populate_CubeY",
	python_callable=_populate_CubeY,
	dag=dag
	)

t1 >> t2 >> t3