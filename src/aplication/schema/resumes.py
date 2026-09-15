"""
models de resumes
"""

from pydantic import BaseModel, Field
from typing import Literal

class CreateResume(BaseModel):

    vancancie_id:int
    status:Literal["aproved", "recuse", "pending"] = Field(default="pending")
    reason:str = Field(default="null")


class GetResume(BaseModel):
    vancancie_id:int|None=Field(default=None)
    id:int|None = Field(default=None)
    get_all:bool = Field(default=False)




