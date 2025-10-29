from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks, Request
from fastapi.responses import StreamingResponse
from fastapi.websockets import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import os, asyncio, json
from typing import Optional, List
from app.database import get_db
from app.models import Project, ProjectStatus, Event, User
from app.schemas import ProjectOut, EventOut
from app.auth import get_current_user
from app.config import settings
from app.services.orchestrator import start_analysis
from app.services.progress import progress_bus
from app.observability.langfuse_client import lf_trace, lf_span

router = APIRouter(prefix="/projects", tags=["projects"])

def ensure_dirs():
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.EXTRACT_DIR, exist_ok=True)

@router.get("", response_model=List[ProjectOut])
def list_projects(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    with lf_trace("projects.list", user_id=str(user.id)):
        items = db.query(Project).filter(Project.owner_id == user.id).order_by(Project.id.desc()).all()
        return items

@router.post("", response_model=ProjectOut)
async def create_project(
    title: Optional[str] = Form(None),
    repo_url: Optional[str] = Form(None),
    personas: Optional[str] = Form("[]"),
    config: Optional[str] = Form("{}"),
    zip: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    ensure_dirs()
    if zip is None and not repo_url:
        raise HTTPException(400, "Provide a ZIP file or a GitHub URL.")

    with lf_trace("projects.create", user_id=str(user.id), metadata={"title": title, "repo_url": repo_url}) as trace:
        project = Project(owner_id=user.id, title=title, repo_url=repo_url, personas=[], config={})
        try:
            project.personas = json.loads(personas or "[]")
            project.config = json.loads(config or "{}")
        except Exception:
            raise HTTPException(400, "Invalid personas/config JSON")

        db.add(project); db.commit(); db.refresh(project)

        if zip is not None:
            content = await zip.read()
            max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
            if len(content) > max_bytes:
                raise HTTPException(413, f"Upload exceeds {settings.MAX_UPLOAD_MB} MB limit")
            upload_path = os.path.join(settings.UPLOAD_DIR, f"project_{project.id}.zip")
            with open(upload_path, "wb") as f:
                f.write(content)
        return project

@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    with lf_trace("projects.get", user_id=str(user.id), metadata={"project_id": project_id}):
        prj = db.query(Project).filter(Project.id == project_id, Project.owner_id == user.id).first()
        if not prj:
            raise HTTPException(404, "Project not found")
        return prj

@router.post("/{project_id}/start")
async def start(project_id: int, background: BackgroundTasks, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    prj = db.query(Project).filter(Project.id == project_id, Project.owner_id == user.id).first()
    if not prj:
        raise HTTPException(404, "Project not found")
    upload_path = os.path.join(settings.UPLOAD_DIR, f"project_{project_id}.zip")
    background.add_task(run_orchestrator_bg, project_id, upload_path)
    return {"message": "Analysis started", "project_id": project_id}

async def run_orchestrator_bg(project_id: int, upload_path: str):
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        prj = db.query(Project).filter(Project.id == project_id).first()
        await start_analysis(db, prj, upload_path if os.path.exists(upload_path) else None)
    finally:
        db.close()

@router.get("/{project_id}/status")
async def status(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    prj = db.query(Project).filter(Project.id == project_id, Project.owner_id == user.id).first()
    if not prj:
        raise HTTPException(404, "Project not found")
    snap = progress_bus.snapshot(project_id)
    return {"project_id": project_id, "status": prj.status.value, **snap}

@router.get("/{project_id}/events", response_model=List[EventOut])
def events(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(Event).filter(Event.project_id == project_id).order_by(Event.id.desc()).limit(200).all()
    return rows

@router.get("/{project_id}/stream")
async def sse_stream(project_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    prj = db.query(Project).filter(Project.id == project_id, Project.owner_id == user.id).first()
    if not prj:
        raise HTTPException(404, "Project not found")

    async def event_generator():
        q = progress_bus.get_queue(project_id)
        yield f"data: {json.dumps(progress_bus.snapshot(project_id))}\n\n"
        while True:
            if await request.is_disconnected():
                break
            try:
                event = await asyncio.wait_for(q.get(), timeout=10.0)
                yield f"data: {json.dumps(event)}\n\n"
            except asyncio.TimeoutError:
                yield ": keep-alive\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.websocket("/{project_id}/ws")
async def websocket_endpoint(websocket: WebSocket, project_id: int):
    await websocket.accept()
    q = progress_bus.get_queue(project_id)
    await websocket.send_json({"type":"snapshot", **progress_bus.snapshot(project_id)})
    try:
        while True:
            event = await q.get()
            await websocket.send_json(event)
    except WebSocketDisconnect:
        pass
