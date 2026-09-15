from src.logs.log import LayerLogger
logger = LayerLogger("aplication").build()


"""
Rotas de resumes
"""
import base64
from fastapi import HTTPException, UploadFile, File, APIRouter, Depends, Form
from fastapi.responses import JSONResponse
from src.service.module import control_db, run_agent
from src.aplication.schema.resumes import GetResume
from src.aplication.dependences.depends import depends_user
from typing import Literal
router_resumes = APIRouter(prefix="/resumes", tags=["resumes"])

@router_resumes.post("/")
async def create_resume(vancancie_id:int=Form(...), pdf:UploadFile=File(...),
                        status:Literal["aproved", "recuse", "pending"]=Form("pending"),
                        reason:str=Form("null"), user:dict|None=Depends(depends_user)) -> JSONResponse:

    try:

        vancancie = await control_db.vancancies.select(search="id", value=vancancie_id)
        if vancancie is None:
            raise HTTPException(
                status_code=401,
                detail="Not found vancancie"
            )

        instance_resume = await control_db.resumes.select(user_id=user["id"], vancancie_id=vancancie_id)
        if instance_resume is not None:
            raise HTTPException(
                status_code=409,
                detail="exists resume"
            )

        

        pdf = await pdf.read()
        result = await control_db.resumes.insert(
            user_id=user["id"],
            vancancie_id=vancancie_id,
            pdf=pdf,
            status=status,
            reason=reason
        )

        run_agent.delay(email=user["email"], resume=pdf, description=vancancie["description"], name_vancancie=vancancie["name"],
                  name_user=user["name"], id=result["id"]
                  )

        

        return JSONResponse(
            status_code=201,
            content={"status": True}
        )

    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=501,
            detail=str(e)
        )


#mostra o resultado da vaga
@router_resumes.get("/")
async def get_resume(resume:GetResume, user:dict|None = Depends(depends_user)) -> JSONResponse:

    try:

        if resume.get_all and (resume.vancancie_id is not None or resume.id is not None):
                raise HTTPException(
                status_code=422,
                detail="if param get_all is True, so not expeted args vancancie_id and id"
            )

        if resume.get_all and user["role"] !="admin":

            raise HTTPException(
                status_code=403,
                detail=f"not permission for user {user['name']}"
            )

        instance_resume = await control_db.resumes.select(
            user_id=user["id"],
            vancancie_id=resume.vancancie_id,
            id=resume.id,
            get_all=resume.get_all
        )

        if instance_resume is None and not resume.get_all:

            raise HTTPException(
                status_code=401,
                detail="Not found resume"
            )

        if resume.get_all:
            for instance in instance_resume:
                instance["created_at"] = str(instance["created_at"])
                instance["pdf"] = base64.b64encode(instance["pdf"]).decode("utf-8")

        else:
            instance_resume["created_at"] = str(instance_resume["created_at"])
            instance_resume["pdf"] = base64.b64encode(instance_resume["pdf"]).decode("utf-8")


        return JSONResponse(
            status_code=201,
            content=instance_resume
        )

    except Exception as e:
        logger.error(e)

        raise HTTPException(
            detail=str(e),
            status_code=501
        )

@router_resumes.delete("/")
async def delete_resume(id:int,vancancie_id:int, user:dict|None = Depends(depends_user)) -> JSONResponse:

    try:

        resume = await  control_db.resumes.select(id=id,vancancie_id=vancancie_id, user_id=user["id"])
        if resume is None:
            raise HTTPException(
                detail="resume not exists",
                status_code=401

            )

        await control_db.resumes.delete(id=id)

        return JSONResponse(
            status_code=201,
            content={"status": True}
        )

    except Exception as e:

        raise HTTPException(
            detail=str(e),
            status_code=501
        )













