"""
Facilita a importação
"""

from src.service.auth import auth_jwt, auth_hash
from src.service.task import task_app
from src.service.db.module import control_db
from src.service.cache.control import client_background
from src.service.utils.sender import sender
from src.service.utils.agent import run_agent


