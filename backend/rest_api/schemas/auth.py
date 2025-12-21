from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class RegisterRequest(BaseModel):
    username: str
    password: str


class RegisterResponse(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    username: str = Field(validation_alias=AliasChoices("username", "login"))
    password: str


class MeResponse(BaseModel):
    id: int
    username: str
