"""
Cria o teste de tasks
"""


from src.config.module import enviroiments
from src.task.celery import TaskControl
app_task = TaskControl(host=enviroiments["redis_host"], port=enviroiments["redis_port"], 
                       password=enviroiments["redis_password"]).run()


@app_task.task()
def task() -> None:

    print("test")


def test_tasks() -> None:


    task.delay()


if __name__ == "__main__":
    import time
    time.sleep(10)
    test_tasks()
