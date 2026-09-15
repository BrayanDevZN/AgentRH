"""
models de auth
"""

from pydantic import BaseModel, Field

class ValidLogin(BaseModel):

    email: str
    password: str|None = Field(default=None)
    code:str|None = Field(default=None)

class ValidUpdatePass(BaseModel):

    password: str|None = Field(default=None)
    new_password: str
    email: str|None = Field(default=None)
    sender: bool = Field(default=False)
    code: str|None = Field(default=None)
    

