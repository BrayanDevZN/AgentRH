"""
models de vancancies
"""

from pydantic import BaseModel
from typing import Literal

class ValidCreateVancancie(BaseModel):
    
    name: str
    description:str


class ValidSelectVancancie(BaseModel):

    search:Literal["all", "id", "created_by", "name"]
    value: str|int|None = None


class ValidSetVancancie(BaseModel):
    search:Literal["id", "name"]
    field:str|int
    set:Literal["name", "description"]
    value:str|int