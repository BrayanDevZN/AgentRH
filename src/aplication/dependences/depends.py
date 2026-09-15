"""
Junção que junta tudo
"""

from src.aplication.dependences.util import UtilsDepends
from fastapi import Request
async def depends_user(request:Request) -> dict:

    instance = UtilsDepends(request=request)

    user = await instance.run()

    return user