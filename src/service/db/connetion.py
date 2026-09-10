"""
Cria a conexão do banco de dados juntando a variavel de ambiente url com o modulo de conexão
"""

from src.config.settings import enviroiments
from src.database.manage import ConenctionDb

engine_session = ConenctionDb(url=enviroiments["url"]).run()