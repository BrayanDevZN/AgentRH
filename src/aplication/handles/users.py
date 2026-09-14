"""
handles de users
"""
from src.logs.log import LayerLogger
logger = LayerLogger("aplication").build()

from fastapi import APIRouter, HTTPException,  Response, Cookie, Depends
from fastapi.responses import JSONResponse
from src.service.module import control_db,  auth_jwt, auth_hash, client_background
from src.aplication.dependences.depends import depends_user
from datetime import timezone, datetime, timedelta
from src.aplication.schema.sender import ValidEmail
from src.aplication.schema.users import ValidPassword, CreateUser, UpdateUser


router_users = APIRouter(prefix="/users", tags=["users"])


#Rota pra criar usuario
@router_users.post("/")
async def create_user(user:CreateUser) -> JSONResponse:
    try:

        email = ValidEmail(email=user.email).email

        exists = await control_db.users.select(search="email", value=email)

        if exists is not None:

            raise HTTPException(
                status_code=409,
                detail="user already exists"
            )

        name=f"email_sender:create:{email}"
        code=await client_background.get(name=name)
        if code is None:
            raise HTTPException(
                status_code=401,
                detail="Expeted code"
            )

        if code != user.code:
            raise HTTPException(
                status_code=404,
                detail="invalid code"
            )

        password = ValidPassword(password=user.password).password
        password = await auth_hash.encode(password=password)

        instance_user = await control_db.users.insert(name=user.name, email=email, age=user.age, cpf=user.cpf,
                                                    password=password, permission=user.permission, gender=user.gender
                                                    )


        expire = datetime.now(timezone.utc) + timedelta(days=7)

        payload = {
            "public_id":str(instance_user["public_id"]),
            "expire": str(expire)
        }

        token = await auth_jwt.encode(payload=payload)

        response = JSONResponse(
            status_code=201,
            content={"status":True}
        )
        response.set_cookie(
            key="X-user_token",
            value=token,
            httponly=True,
            samesite="strict"
        )
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao criar usuário: {e}")
        raise HTTPException(
            status_code=500,
            detail=e
        )


#Rota pra pegar os dados do usaurio
@router_users.get("/")
async def get_user(user:dict=Depends(depends_user)) -> JSONResponse:

    try:

        user["public_id"] = str(user["public_id"])
        user["created_at"] = str(user["created_at"])

        return JSONResponse(
            status_code=201,
            content=user
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao buscar usuário: {e}")

        raise HTTPException(
            status_code=500,
            detail=e
        )


#Rota pra atualizar algum dado do usuario
@router_users.patch("/")
async def update_user(update:UpdateUser,cookie:str|None = Cookie(default=None, alias="X-user_token")) -> JSONResponse:

    try:

        if cookie is None:

            raise HTTPException(
                status_code=404,
                detail="Expeted X-user_token"

            )


        token = await auth_jwt.decode(cookie)

        now = datetime.now(timezone.utc)
        if now > datetime.strptime(token["expire"], "%Y-%m-%d %H:%M:%S.%f%z"):

            raise HTTPException(
                detail="Expired token",
                status_code=409
            )


        await control_db.users.update(search="public_id", field=token["public_id"], set=update.set, value=update.value)


        return JSONResponse(
            status_code=201,
            content={"status":True}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao atualizar usuário: {e}")

        raise HTTPException(
            status_code=500,
            detail=e
        )

#Deleta o usuario
@router_users.delete("/")
async def delete_user( response:Response,password:ValidPassword,user:dict = Depends(depends_user)) -> JSONResponse:

    try:

        password = password.password

        password_db =user["password"]

        if not await auth_hash.check(password=password, hashed_passowrd=password_db):

            raise HTTPException(
                status_code=401,
                detail="Invalid pass"
            )

        await control_db.users.delete(public_id=user["public_id"])
        response.delete_cookie(
            key="X-user_token"
        )

        return JSONResponse(
            status_code=201,
            content={"status":True}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao deletar usuário: {e}")

        raise HTTPException(
            status_code=500,
            detail="internal server error"
        )







        





    
