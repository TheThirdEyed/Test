
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any

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

class ProjectOut(BaseModel):
    id: int
    name: str
    status: str
    personas: str
    repo_source: str
    repo_url: Optional[str] = None

class AgentStartIn(BaseModel):
    project_id: int
    depth: str = "standard"
    verbosity: str = "standard"
    personas: str = "SDE,PM"
    diagram_prefs: Optional[str] = None
    repo_url: Optional[str] = None

class QAIn(BaseModel):
    project_id: int
    persona: str = "SDE"
    question: str

class QAOut(BaseModel):
    markdown: str
    sources: List[Any] = []
