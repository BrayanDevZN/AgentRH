"""
junta os modulos de auth e instancia eles
"""

from src.config.settings import enviroiments
from src.auth.module import AuthJwt, AuthHash


auth_jwt = AuthJwt(sing=enviroiments["sing"])
auth_hash = AuthHash()