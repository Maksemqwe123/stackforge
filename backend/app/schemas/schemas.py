from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models import DeployStatus


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class StackCreate(BaseModel):
    name: str = Field(min_length=2, max_length=128)
    compose_path: str


class StackOut(BaseModel):
    id: int
    name: str
    compose_path: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DeploymentOut(BaseModel):
    id: int
    stack_id: int
    status: DeployStatus
    logs: str
    created_at: datetime

    model_config = {"from_attributes": True}
