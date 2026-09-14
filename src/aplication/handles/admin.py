from src.logs.log import LayerLogger
logger = LayerLogger("aplication").build()

"""
Rota de admin
"""

from src.aplication.dependences.depends import depends_user
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from src.service.module import control_db,  enviroiments
from src.aplication.schema.admin import ValidAddPermission, ValidGetUser, ValidDeleteUser

router_admin = APIRouter(prefix="/admin", tags=["admin"])


#Rota pra fazer um usuario virar admin
@router_admin.patch("/")
async def alter_permission(set_user:ValidAddPermission,user: dict|None = Depends(depends_user)) -> JSONResponse:

    try:

        role = set_user.value
        required_user = await control_db.users.select(search=set_user.search, value=set_user.field)
        if required_user is None:
             raise HTTPException(
                  status_code=401, 
                  detail=f"Not found user"
             )
        if required_user["role"] == "admin" and user["email"] != enviroiments["email_user"]:


                raise HTTPException(
                    status_code=403,
                    detail=f"Not permission for {user["name"]}"
                )

        if role == required_user["role"]:
             raise HTTPException(
                  status_code=401,
                  detail=f"{user["name"]} is already an {role}"
             )


        await control_db.users.update(search=set_user.search, field=set_user.field, set="role", value=set_user.value)

        return JSONResponse(
             status_code=201,
             content={"status":True}
        )


    except Exception as e:
         logger.error(e)
         raise HTTPException(
              status_code=501,
              detail=e
         )



#Rota serve para ver os usuarios
@router_admin.get("/")
async def get_users(get_user:ValidGetUser, user:dict|None = Depends(depends_user)) -> JSONResponse:

     try:

          if get_user.is_all and (get_user.search or get_user.value):

               raise HTTPException(
                    status_code=401,
                    detail="if param is_all is True, not expeted params search and value"
               )

          
          get_user = await control_db.users.select(search=get_user.search, value=get_user.value,
                                                        is_all=get_user.is_all, 
                                                        is_admin=user["email"] == enviroiments["email_user"])

          if get_user is not None:
               get_user["public_id"] = str(get_user["public_id"])
               get_user["created_at"] = str(get_user["created_at"])

          return JSONResponse(
               status_code=201,
               content=get_user
          )

     except Exception as e:
          logger.error(e)
          raise HTTPException(
               status_code=501,
               detail=e
          )


#Rota que o admin pode deletar o usuario
@router_admin.delete("/")
async def delete_user(get_user:ValidDeleteUser, user:dict|None = Depends(depends_user)) -> JSONResponse:

     try:

          if user["email"] != enviroiments["email_user"]:

               raise HTTPException(
                    status_code=403,
                    detail=f"Not permission for user {user["name"]}"
               )


          get_user = await control_db.users.select(search=get_user.search, value=get_user.value)
          if get_user is None:
               raise HTTPException(
                    status_code=401,
                    detail="Not found user"
               )


          await control_db.users.delete(public_id=get_user["public_id"])

          return JSONResponse(
               status_code=201,
               content={"status": True}
          )

     except Exception as e:

          logger.error(e)
          raise HTTPException(
               detail=e,
               status_code=501
          )

        
