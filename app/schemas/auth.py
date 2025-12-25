from .base import BaseSchema

class Token(BaseSchema):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseSchema):
    email: str | None = None
    role: str | None = None