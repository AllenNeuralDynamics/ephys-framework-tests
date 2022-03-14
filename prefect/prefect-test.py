from prefect import task, Flow, Parameter
from prefect.storage import GCS
from prefect.run_configs import VertexRun

@task
def task_1(x):
    return x

@task
def task_2(x):
    return x

@task
def task_3(x):
    return x

storage = GCS('prefect-artifacts', stored_as_script=True)
run_config = VertexRun(image='prefecthq/prefect:latest')

with Flow('vertex-test', storage=storage, run_config=run_config) as flow:

    p = Parameter('x', default=1)
    
    for i in range(5):
        vi = task_1(p)

        for j in range(5):
            vj = task_2(vi)

            for k in range(5):
                vk = task_3(vj)

            
