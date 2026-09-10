"""
pega as variaveis de ambiente e instancia tasks
"""

from src.config.settings import enviroiments
from src.task.celery import TaskControl

task_app = TaskControl(port=enviroiments["redis_port"], host=enviroiments["redis_host"], 
                       password=enviroiments["redis_password"]).run()



task_app.conf.imports = (
    "src.service.cache.task", "src.service.utils.sender", "src.service.utils.agent"
)