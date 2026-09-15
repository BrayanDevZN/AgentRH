from src.logs.log import LayerLogger
logger = LayerLogger("aplication").build()
"""
handles de auth
"""

from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, Request, Response, status, Cookie, Depends
from src.service.module import control_db, auth_hash,auth_jwt, client_background
from datetime import timezone, datetime, timedelta
from src.aplication.schema.users import ValidPassword
from src.aplication.schema.sender import ValidEmail
from src.aplication.schema.auth import ValidLogin, ValidUpdatePass
from src.aplication.dependences.depends import depends_user
router_auth = APIRouter(prefix="/auth", tags=["auth"])


#Rota para fazer login
@router_auth.get("/")
async def user_login(user:ValidLogin, request:Request, response:Response) -> JSONResponse:

    try:

        email = ValidEmail(email=user.email).email
    
        

        cookie = request.cookies.get("X-auth2_token")
        
        if cookie is not None:
            token_auth = await auth_jwt.decode(token=cookie)
            
            now = datetime.now(timezone.utc)
            expire = datetime.strptime(token_auth["expire"], "%Y-%m-%d %H:%M:%S.%f%z")
            if now>expire:
                raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="expired X-auth2_token"
            )
            if user.code is None:

                raise HTTPException(
                    status_code=401,
                    detail="expeted code"
                )
            
            code_auth = await client_background.get(f"email_sender:auth:{email}")
            if user.code != code_auth:
                raise HTTPException(
                    status_code=404,
                    detail="Invalid code"
                )

            await client_background.delete(name=f"email_sender:auth:{email}")

            response = JSONResponse(
                status_code=201,
                content={"status":True, "auth": True}
            )
            response.delete_cookie("X-auth2_token")

            expire = datetime.now(timezone.utc) + timedelta(days=7)

            token = {
                "public_id": str(token_auth["public_id"]),
                "expire": str(expire)
            }

            token = await auth_jwt.encode(payload=token)
            response.set_cookie(
                key="X-user_token",
                value=token,
                httponly=True,
                samesite="strict",
            
            )

            payload = {
                    "created_at": str(now),
                    "public_id": str(token_auth["public_id"])
                }
            token = await auth_jwt.encode(payload=payload)
            response.set_cookie(
                    key="X-user_refresh_token",
                    value=token,
                    httponly=True,
                    samesite="strict"
                )


            return response


        else:

        


            instance_user = await control_db.users.select(search="email", value=email)

    
            if instance_user is None:

                raise HTTPException(
                    status_code=401,
                    detail="User not Found"
                )

            if instance_user["role"] == "user" and user.password is None:
                raise HTTPException(
                    status_code=401,
                    detail="if user role is user, expeted password"
                )

        

            if instance_user["password"] is not None:
                password = ValidPassword(password=user.password).password

                check = await auth_hash.check(password=password, hashed_passowrd=instance_user["password"])
                if not check:
                    raise HTTPException(
                        status_code=404,
                        detail="Invalid password"
                    )
                
            

            


            if instance_user["permission"]:

                expire = datetime.now(timezone.utc) + timedelta(minutes=8)


                payload = {
                    "email": email,
                    "public_id": str(instance_user["public_id"]),
                    "expire": str(expire),
                    "name": instance_user["name"]
                }

                token = await auth_jwt.encode(payload=payload)

                response = JSONResponse(
                    status_code=201,
                    content={
                        "status": True,
                        "auth": "required"
                    }
                )

                response.set_cookie(
                    value=token,
                    key="X-auth2_token",
                    samesite="strict",
                    httponly=True,
                    max_age=60 * 5
                )

                return response

            else:


                response = JSONResponse(
                    status_code=201,
                    content={"status":True, "auth": False}
                )

                expire = datetime.now(timezone.utc) + timedelta(days=7)

                token = {
                    "public_id": str(token_auth["public_id"]),
                    "expire": str(expire)
                }

                token = await auth_jwt.encode(payload=token)
                response.set_cookie(
                    key="X-user_token",
                    value=token,
                    httponly=True,
                    samesite="strict",
                    
                )

                payload = {
                    "created_at": str(now),
                    "public_id": str(token_auth["public_id"])
                }
                token = await auth_jwt.encode(payload=payload)
                response.set_cookie(
                    key="X-user_refresh_token",
                    value=token,
                    httponly=True,
                    samesite="strict"
                )

            return response

    except Exception as e:
        logger.error(e)
        raise HTTPException(
            detail=str(e),
            status_code=501
        )


#Rota pra atualizar senha do usuario
@router_auth.patch("/")
async def user_update_pass(request:Request,user:ValidUpdatePass, cookie = Cookie(default=None, alias="X-user_token")) -> JSONResponse:

    try:

        instance_user = await depends_user(request=request) if not user.sender else await control_db.users.select(search="email", value=user.email)

        new_pass = ValidPassword(password=user.new_password).password

        if user.sender:

            if user.new_password is not None:
                raise HTTPException(
                    detail="Not expeted  new_password if param auth is True", status_code=401
                )

            if user.code is None:
                raise HTTPException(
                    detail="Expeted code if param sender is True", status_code=401
                )
            if user.email is None:
                raise HTTPException(
                    detail="Expeted email if param sender is True", status_code=401
                )

            email = ValidEmail(email=user.email).email


            user_code = await client_background.get(name=f"user_sender:update:{email}")

            if user_code is None:
                raise HTTPException(
                    detail="Expires code", status_code=401
                )

            if user_code != user.code:
                raise HTTPException(
                    detail="Invalid code", status_code=404
                )


        else:
            if cookie is None:
                raise HTTPException(
                    status_code=401,
                    detail="Expeted token X-user_token if param sender is False"
                )

            if user.password is None:
                raise HTTPException(
                    status_code=401,
                    detail="Expeted password if param sender is False"
                )

            check = await auth_hash.check(password=user.password, hashed_passowrd=instance_user["password"])
            if not check:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid pass"
                )

        check = await auth_hash.check(password=new_pass, hashed_passowrd=instance_user["password"])
        if check:
            raise HTTPException(
                status_code=401,
                detail="equal password"
            )

        hashed_new_pass = await auth_hash.encode(password=new_pass)

        await control_db.users.update(
            search="id",
            field=instance_user["id"],
            set="password",
            value=hashed_new_pass
        )

        response = JSONResponse(
            status_code=201,
            content={"status": True}
        )

        if cookie is not None:
            response.delete_cookie(
                key="X-user_token"
            )

        return response

    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=501,
            detail=str(e)
        )


#Rota que faz logout e deleta o token
@router_auth.delete("/")
async def logout(user:dict|None = Depends(depends_user)) -> JSONResponse:


    try:

        response = JSONResponse(
            status_code=201,
            content={"status": True}
        )
        response.delete_cookie(key="X-user_token")
        response.delete_cookie(key="X-user_refresh_token")

        return response

    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=501,
            detail=str(e)
        )


#Rota pra atualizar o X-user_token
@router_auth.put("/")
async def refresh(user:dict|None = Depends(depends_user), 
                  cookie:str|None = Cookie(default=None, alias="X-user_refresh_token")) -> JSONResponse:

    try:

        if cookie is None:
            raise HTTPException(
                status_code=401,
                detail="Expeted X-user_refresh_token"
            )

        refresh = await auth_jwt.decode(token=cookie)

        if str(refresh["public_id"]) != str(user["public_id"]):
            raise HTTPException(
                status_code=409,
                detail="Invalid refresh token"
            )

        payload = await auth_jwt.decode(token=cookie)

        now = datetime.now(timezone.utc)
        expire = datetime.strptime(payload["expire"], "%Y-%m-%d %H:%M:%S.%f%z")
        if not now>expire:
            raise HTTPException(
                status_code=501,
                detail="X-user_token not expired"
            )

        

        response = JSONResponse(
            status_code=201,
            content={"status":True}
        )



        payload = {
            "public_id": user["public_id"],
            "expire": str(now + timedelta(days=7))
        }

        token = await auth_jwt.encode(payload=payload)

        response.set_cookie(
            key="X-user_token",
            value=token,
            samesite="strict",
            httponly=True
            
        )

        payload = {
            "created_at": now,
            "public_id": user["public_id"]
        }

        token = await auth_jwt.encode(payload=payload)

        response.set_cookie(
            key="X-user_refresh_token",
            value=token,
            httponly=True,
            samesite="strict"
        )

        return response

    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=501,
            detail=str(e)
        )



        
        

        


        

            






        

