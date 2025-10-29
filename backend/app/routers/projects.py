
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
from typing import Optional
import os

from ..database import get_db
from ..models import Project, ActivityEvent
from ..schemas import ProjectOut
from ..config import settings
from ..utils.zip_utils import validate_and_extract_zip
from ..utils.git_utils import clone_repo

DATA_ROOT = "/app/data"
router = APIRouter(prefix="/projects", tags=["projects"])
os.makedirs(DATA_ROOT, exist_ok=True)

@router.post("", response_model=ProjectOut)
def create_project(
    name: str = Form(...),
    personas: str = Form("SDE,PM"),
    repo_url: Optional[str] = Form(None),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):
    if repo_url and file:
        raise HTTPException(status_code=400, detail="Provide either repo_url or file, not both")
    project = Project(owner_id=1, name=name, personas=personas, repo_source="git" if repo_url else "upload", repo_url=repo_url, status="created")
    db.add(project); db.commit(); db.refresh(project)

    proj_path = os.path.join(DATA_ROOT, f"project_{project.id}")
    os.makedirs(proj_path, exist_ok=True)

    if file:
        try:
            validate_and_extract_zip(file, proj_path, max_mb=settings.MAX_UPLOAD_MB)
        except HTTPException as e:
            project.status = "failed"; db.commit(); raise e
    elif repo_url:
        ok, msg = clone_repo(repo_url, proj_path)
        if not ok:
            project.status = "failed"; db.commit(); raise HTTPException(status_code=400, detail=msg)

    db.add(ActivityEvent(project_id=project.id, stage="init", message="Project created", level="info"))
    project.status = "queued"; db.commit()
    return ProjectOut(id=project.id, name=project.name, status=project.status, personas=project.personas, repo_source=project.repo_source, repo_url=project.repo_url)
