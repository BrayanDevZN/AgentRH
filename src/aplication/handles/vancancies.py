from src.logs.log import LayerLogger
logger = LayerLogger("aplication").build()


"""
Rotas de vancancies
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from src.service.module import control_db
from src.aplication.dependences.depends import depends_user
from src.aplication.schema.vancancies import ValidCreateVancancie, ValidSelectVancancie, ValidSetVancancie
router_vancancies = APIRouter(prefix="/vancancies", tags=["vancancies"])


@router_vancancies.post("/")
async def create_vancancie(vancancie:ValidCreateVancancie, user:dict|None=Depends(depends_user)) -> JSONResponse:

    try:

        exists = await control_db.vancancies.select(search="name", value=vancancie.name)

        if exists is not None:

            raise HTTPException(
                status_code=409,
                detail=f"{vancancie.name} exists"
            )

        instance_vancancie = await control_db.vancancies.insert(created_by=user["id"],
                                                                name=vancancie.name, description=vancancie.description)


        del instance_vancancie["created_by"]

        instance_vancancie["created_at"] = str(instance_vancancie["created_at"])


        return JSONResponse(
            status_code=201,
            content=instance_vancancie
        )

    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=501,
            detail=e
        )


#Busca as vagas
@router_vancancies.get("/")
async def get_vancancie(vancancie:ValidSelectVancancie, user:dict|None=Depends(depends_user)) -> JSONResponse:
    try:

        if vancancie.search == "all":

            if vancancie.value is not None:

                raise HTTPException(
                    status_code=401,
                    detail="param search is all, so not expeted param value"
                )

            instance_vancancie = await control_db.vancancies.select(search=vancancie.search)

        else:

            if vancancie.value is None:
                raise HTTPException(
                    status_code=401,
                    detail="Expeted param value"
                )

            instance_vancancie = await control_db.vancancies.select(search=vancancie.search, value=vancancie.value)

        if user["role"] != "admin":
            del instance_vancancie["created_by"]

        instance_vancancie["created_at"] = str(instance_vancancie["created_at"])

        return JSONResponse(
            status_code=201,
            content=instance_vancancie
        )

    except Exception as e:
        logger.error(e)
        raise HTTPException(
            detail=e,
            status_code=501
        )


#atualiza informção da vaga
@router_vancancies.patch("/")
async def update_vancancie(vancancie:ValidSetVancancie, user:dict|None = Depends(depends_user)) -> JSONResponse:

    try:

        vancancie = await control_db.vancancies.update(search=vancancie.search, field=vancancie.field,
                                                       set=vancancie.set, value=vancancie.value)


        if vancancie is None:

            raise HTTPException(
                status_code=401,
                detail=f"Not exists vancancie"
            )

        vancancie["created_at"] = str(vancancie["created_at"])


        return JSONResponse(
            status_code=201,
            content=vancancie
        )

    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=501,
            detail=e
        )


#Rota pra deletar vaga
@router_vancancies.delete("/")
async def del_vancancie(vancancie:ValidSetVancancie, user:dict|None = Depends(depends_user)) -> JSONResponse:

    try:

        vancancie = await control_db.vancancies.update(search=vancancie.search, field=vancancie.field,
                                                       set=vancancie.set, value=vancancie.value)


        if vancancie is None:

            raise HTTPException(
                status_code=401,
                detail=f"Not exists vancancie"
            )

        await control_db.vancancies.delete(id=vancancie["id"])

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






        


        