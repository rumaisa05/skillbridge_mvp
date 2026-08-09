from pydantic import BaseModel, EmailStr
from typing import Literal


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: Literal["participant", "organization"] = "participant"


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    role: str
    bio: str = ""
    skills: str = "[]"
    github_url: str = ""

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: str | None = None
    bio: str | None = None
    skills: str | None = None
    github_url: str | None = None
    avatar_url: str | None = None


class Login(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
