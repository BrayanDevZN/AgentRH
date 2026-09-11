"""
Confere se o usuario existe e pega o token
"""

from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
from src.service.module import control_db, auth_jwt
from datetime import datetime, timedelta,timezone
class UtilsDepends:

    def __init__(self, request:Request)-> None:

        self.requst = request


    #Pega o token e decodifica
    async def _token(self)-> None:

        cookie = self.requst.cookies.get("X-instance_user")

        self.payload = await auth_jwt.decode(token=cookie)

    #Confere se o token ainda é valido
    async def _valid(self) -> None:

        now = datetime.now(timezone.utc)
        expire = datetime.strptime(self.payload["expire"], timezone.utc)
        if now > expire:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="expired token"
            )


    #Busca o usuario e levanta erro se não existir
    async def _user(self) -> None:

        self.user = await  control_db.users.select(search="public_id", value=self.payload["public_id"])

        if self.user is None:

            raise HTTPException(
                status_code=401,
                detail="not found user"
            )


    #Executa os metodos e retorna os dados do usuario
    async def run(self) -> dict:

        await self._token()
        await self._valid()
        await self._user()

        return self.user
    





    
        