"""
Junta todos os modulos
"""

from src.service.db.vancancies import ControlVancancies
from src.service.db.users import ControlUsers
from src.service.db.resumes import ControlResumes
from src.service.db.migration import migration_tables

class ControlDb:

    def __init__(self)-> None:

        self.users = ControlUsers()
        self.resumes = ControlResumes()
        self.vancancies = ControlVancancies()



control_db = ControlDb()
        