
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import AgentRun, DocArtifact, CodeChunk, Project
from ..schemas import AgentStartIn, QAIn, QAOut
from .analysis import ANALYSIS_STATE
from ..services.agents.coordinator import run_pipeline
from ..services.qna import answer_question
import os, asyncio

router = APIRouter(prefix="/agents", tags=["agents"])

@router.post("/start")
def start_agents(payload: AgentStartIn, bg: BackgroundTasks, db: Session = Depends(get_db)):
    proj = db.get(Project, payload.project_id)
    if not proj: raise HTTPException(status_code=404, detail="Project not found")
    proj_path = f"/app/data/project_{proj.id}"
    if not os.path.exists(proj_path): raise HTTPException(status_code=400, detail="Project data missing; upload or clone first")

    run = AgentRun(project_id=payload.project_id, status="running", depth=payload.depth, verbosity=payload.verbosity)
    db.add(run); db.commit(); db.refresh(run)

    async def job():
        pid = payload.project_id
        ANALYSIS_STATE[pid] = {"status":"processing","progress":0,"paused":False}
        # preprocessing phase (simulate %)
        for _ in range(5):
            await asyncio.sleep(0.8)
            if ANALYSIS_STATE[pid]["paused"]: continue
            ANALYSIS_STATE[pid]["progress"] += 5
        # run pipeline
        await run_pipeline(db, pid, proj_path, personas=payload.personas)
        ANALYSIS_STATE[pid]["progress"] = 100
        run.status = "completed"; db.commit()

    bg.add_task(job)
    return {"agent_run_id": run.id, "status": "running"}

@router.post("/pause/{project_id}")
def pause(project_id: int):
    st = ANALYSIS_STATE.get(project_id)
    if not st: raise HTTPException(status_code=404, detail="No analysis for project")
    st["paused"] = True; return {"ok": True}

@router.post("/resume/{project_id}")
def resume(project_id: int):
    st = ANALYSIS_STATE.get(project_id)
    if not st: raise HTTPException(status_code=404, detail="No analysis for project")
    st["paused"] = False; return {"ok": True}

@router.get("/artifacts/{project_id}")
def list_artifacts(project_id: int, db: Session = Depends(get_db)):
    rows = db.query(DocArtifact).filter(DocArtifact.project_id==project_id).all()
    return [{"id": r.id, "title": r.title, "persona": r.persona} for r in rows]

@router.get("/artifact/{artifact_id}")
def get_artifact(artifact_id: int, db: Session = Depends(get_db)):
    r = db.get(DocArtifact, artifact_id)
    if not r: raise HTTPException(status_code=404, detail="Not found")
    return {"id": r.id, "title": r.title, "persona": r.persona, "content_md": r.content_md}

@router.post("/ask", response_model=QAOut)
async def ask(q: QAIn, db: Session = Depends(get_db)):
    return await answer_question(db, q.project_id, q.question, q.persona)
