"""
Junta os modulos e facilita a importação
"""


#Importa a conexão do banco
from src.database.connection.engine import ConenctionDb



#Importa a função que cria as tabelas do banco
from src.database.migration.tables import migration_db


#Junta os 3 modulos de repository em um
from sqlalchemy.ext.asyncio import AsyncEngine
from src.database.repository.users import UsersDb, Users
from src.database.repository.vancancies import VancanciesDb, Vancancies
from src.database.repository.resumes import ResumesDb, Resumes

class ControlDb:

    def __init__(self, engine:AsyncEngine)-> None:

        self.users = UsersDb(engine)
        self.vancancies = VancanciesDb(engine)
        self.resumes = ResumesDb(engine)


