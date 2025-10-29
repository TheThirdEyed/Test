
from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "User"

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class ProjectCreate(BaseModel):
    name: str
    personas: str = "SDE,PM"
    repo_url: Optional[str] = None

class ProjectOut(BaseModel):
    id: int
    name: str
    status: str
    personas: str
    repo_source: str
    repo_url: Optional[str] = None
