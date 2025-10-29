from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Project
from app.auth import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users")
def list_users(db: Session = Depends(get_db), admin = Depends(require_admin)):
    return db.query(User).order_by(User.id.desc()).all()

@router.get("/projects")
def list_projects(db: Session = Depends(get_db), admin = Depends(require_admin)):
    return db.query(Project).order_by(Project.id.desc()).all()
