from pydantic import BaseModel, EmailStr
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime
from app.models import RoleEnum, ProjectStatus, EventLevel

class SignupIn(BaseModel):
    email: EmailStr
    password: str
    role: RoleEnum = RoleEnum.user

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ProjectOut(BaseModel):
    id: int
    title: Optional[str] = None
    status: ProjectStatus
    personas: List[str] = []
    repo_url: Optional[str] = None
    created_at: datetime
    owner_id: int
    class Config:
        from_attributes = True

class EventOut(BaseModel):
    id: int
    project_id: int
    ts: datetime
    level: EventLevel
    stage: Optional[str] = None
    message: str
    payload: Dict[str, Any] = {}
    class Config:
        from_attributes = True
