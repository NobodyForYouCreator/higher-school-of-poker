from pydantic import BaseModel


class RegisterRequest(BaseModel):
    username: str
    password: str


class RegisterResponse(BaseModel):
    access_token: str
    token_type: str