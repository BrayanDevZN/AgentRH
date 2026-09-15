"""
models de admin
"""

from pydantic import BaseModel, Field
from typing import Literal
class ValidAddPermission(BaseModel):

    search: Literal["email", "cpf", "id", "public_id"]
    field: str|int
    value: Literal["admin", "user"]


class ValidGetUser(BaseModel):

    is_all: bool = Field(default=False)
    search: Literal["email", "cpf", "id", "public_id"] = Field(default=None)
    value: str|int = Field(default=None)

class ValidDeleteUser(BaseModel):

    search: Literal["email", "cpf", "id", "public_id"] 
    value: str|int 



