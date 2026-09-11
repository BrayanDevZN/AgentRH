"""
Handles de sender
"""

from fastapi import HTTPException, APIRouter, Depends, Cookie, status
from src.aplication.dependences.depends import depends_user
from src.service.module import senders, sender, client_background, control_db, auth_jwt
from src.aplication.schema.sender import ValidEmail, SenderCreate
from fastapi.responses import JSONResponse
from datetime import timezone, datetime
import secrets
router_sender = APIRouter(prefix="/sender", tags=["sender"])

@router_sender.post("/")
async def sender_create(user: SenderCreate) -> JSONResponse:

    try:

        email = ValidEmail(email=user.email).email
        name = user.name
        secret = str(secrets.randbelow(90000) + 10000)
       
        
        secret = str(secrets.randbelow(90000) + 10000)
        name_set = f"email_sender:create:{email}"
        await client_background.set(name=name_set, data=secret, ttl=60 * 15)
        html = str(senders["create_account"])
        body = html.format(name, secret)
        sender.delay(email=email, subject="Codigo para criação de conta!!", body=body)

        return JSONResponse(
            status_code=201,
            content={"status": True}
        )

    except Exception:

        raise HTTPException(
            status_code=501, 
            detail="internal server error"
        )


@router_sender.patch("/")
async def sender_update(email:SenderCreate) -> JSONResponse:

    try:

        user = await control_db.users.select(search="email", value=email)

        if user is None:

            raise HTTPException(
                status_code=401,
                detail="Not found user"
            )



        email = ValidEmail(email).email
        name = user["name"]

        secret = str(secrets.randbelow(90000) + 10000)
        await client_background.set(name=f"email_sender:update:{email}", data=secret, ttl=60 * 8)

        html = str(senders["update_password"])
        body = html.replace(name, secret)

        sender.delay(email=email, subject="Codigo para alterar senha!!", body=body)

        return JSONResponse(
            status_code=201,
            content={"status": True}
        )

    except Exception:

        raise HTTPException(
            status_code=501, 
            detail="internal server error"
        )


@router_sender.post("/2fa")
async def sender_auth(cookie:str|None = Cookie(default=None)) -> JSONResponse:

    try:

        if cookie is None:

            raise HTTPException(
                status_code=401,
                detail="expeted cookie"
            )

        if not "X-auth2_token" in cookie:

            raise HTTPException(
                status_code=401,
                detail="expeted token X-auth2_token"
            )

        payload = await auth_jwt.decode(token=cookie["X-auth2_token"])
        now = datetime.now(timezone.utc)
        expire = datetime.strptime(payload["expire"], timezone.utc)
        if now > expire:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="expired X-auth2_token"
            )

        name = payload["name"]
        email = payload["email"]



        

        secret = str(secrets.randbelow(90000) + 10000)

        await client_background.set(f"email_sender:auth:{email}", data=secret)

        html = str(senders["two_factor_authentication"])
        body = html.format(name, secret)

        sender.delay(email=email, subject="Codigo de autentificação de dois fatores", body=body)


        return JSONResponse(
            status_code=201,
            content={"status": True}
        )

    except Exception:

        raise HTTPException(
            status_code=501, 
            detail="internal server error"
        )





        














