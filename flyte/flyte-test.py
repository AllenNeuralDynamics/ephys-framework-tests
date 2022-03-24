from flytekit import task, workflow
from typing import List

@task
def task_1(x: int) -> int:
    return x+1

@task
def task_2(x: int) -> int:
    return x+2

@task
def task_3(x: int) -> int:
    return x+3

@task 
def task_4(x: List[int]) -> int:
    return sum(x)

@workflow
def run_workflow(p: int) -> int:
    o = []

    for i in range(5):
        vi = task_1(x=p)

        for j in range(5):
            vj = task_2(x=vi)

            for k in range(5):
                vk = task_3(x=vj)

                o.append(vk)

    result = task_4(x=o)

    return result


if __name__ == "__main__":
    print(run_workflow(p=10))

    

            
