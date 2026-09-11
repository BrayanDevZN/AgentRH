"""
Esse midlleware vai conferir o rate limit e rate limit global
"""
from fastapi import Request,  HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from src.service.module import enviroiments, client_background




class Midlleware(BaseHTTPMiddleware):

    #Confere o rate limit global
    async def _global(self) -> None|JSONResponse:

        name = f"global_rate_limit"

        instance = await client_background.get(name=name)

        if instance is None:
            await client_background.increment(name)
            return None
        

        limit = enviroiments["global_rate_limit"]

        if instance > limit:

            return JSONResponse(
                status_code=429,
                content={"error": "exceded global rate limit"}
            )


        await client_background.increment(name)
        return None


    #confere o rate limit
    async def _limit(self, requests:Request) -> None|JSONResponse:

        #Rotas publicas
        PUBLIC_ROUTES = {
            "/users/": ["POST"], "/senders/": ["PATCH", "POST"]
        }

        if requests.url.path in PUBLIC_ROUTES.keys() and requests.method in PUBLIC_ROUTES[requests.url.path]:

            name = f"rate_limit:{requests.client.host}"

        else:

            token = requests.cookies.get("X-user_token")

            if token is None:

                return HTTPException(
                    status_code=404,
                    detail="exepeted X-user_token in headers"
                )

            name = f"rate_limit:{token}"

        instance = await client_background.get(name)

        if instance is None or enviroiments["rate_limit"] > instance:
            await client_background.increment(name)
            return None

        elif instance is not None and enviroiments["rate_limit"]<instance:

            return JSONResponse(
                content={"error": "execeded rate limit"}, status_code=422
            )

    async def dispatch(self, request:Request, call_next):

        global_rate_limit = await self._global()

        if global_rate_limit is not None:
            return global_rate_limit

        rate_limit = await self._limit(requests=request)

        if rate_limit is not None:

            return rate_limit

        return await call_next(request)
        



        


        


