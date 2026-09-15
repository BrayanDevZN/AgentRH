"""
schema de users
"""


from pydantic import BaseModel, Field, field_validator
from typing import Literal
class CreateUser(BaseModel):
    name:str
    email:str
    cpf:str = Field(min_length=11, max_length=11)
    age:int = Field(ge=18)
    password:str = Field(min_length=8)
    gender:Literal["male", "female", "other"]
    permission:bool = Field(default=False)
    code:str

class ValidPassword(BaseModel):
    password: str = Field(min_length=8)

    @field_validator("password")
    def valid(cls, password:str) -> str:

        if not any( c.isupper() for c in password):

            raise ValueError("Expeted min  1 supper caracter in password")

        if not any(c.islower() for c in password):

            raise ValueError("Expeted min 1 lower caracter in password")

        if not any(c.isalpha() for c in password):

            raise ValueError("Expeted min 1 alpha caracter in password")

        if not any(c.isdigit() for c in password):

            raise ValueError("Expeted min 1 digit caracter in password")

        return password

class UpdateUser(BaseModel):

    set:Literal["permission", "age", "gender"]
    value:bool|int|str






