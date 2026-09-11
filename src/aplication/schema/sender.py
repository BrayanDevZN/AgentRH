"""
schema de sender
"""
from pydantic import field_validator, BaseModel

class SenderCreate(BaseModel):

    name:str
    email:str


class ValidEmail(BaseModel):

    email:str

    @field_validator("email")
    def valid(cls, email:str) -> str:

        if not "@gmail.com" in email:

            raise ValueError(f"Expeted @hmail.com in {email}")

        email_copy = email.replace("@gmail.com", "")

        if len(email_copy) < 8:

            raise ValueError(f"Expeted min length 8 in {email}")

        return email


