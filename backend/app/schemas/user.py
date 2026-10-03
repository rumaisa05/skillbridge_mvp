from pydantic import BaseModel, EmailStr, field_validator
from typing import Literal


def _clean_email(value):
    """Trim whitespace and lower-case, so 'Ngo@X.com ' and 'ngo@x.com' are the same account."""
    return value.strip().lower() if isinstance(value, str) else value


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: Literal["participant", "organization"] = "participant"

    @field_validator("email", mode="before")
    @classmethod
    def _normalise_email(cls, value):
        return _clean_email(value)


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    role: str
    bio: str = ""
    skills: str = "[]"
    github_url: str = ""
    org_type: str = ""
    website: str = ""

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: str | None = None
    bio: str | None = None
    skills: str | None = None
    github_url: str | None = None
    avatar_url: str | None = None
    org_type: str | None = None
    website: str | None = None


class Login(BaseModel):
    email: str
    password: str

    @field_validator("email", mode="before")
    @classmethod
    def _normalise_email(cls, value):
        return _clean_email(value)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
