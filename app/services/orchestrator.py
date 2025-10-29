import asyncio, os, json
from typing import Optional
from sqlalchemy.orm import Session
from app.models import Project, ProjectStatus, Event
from app.services.progress import progress_bus
from app.config import settings
from app.utils import validate_and_extract_zip
from app.observability.langfuse_client import lf_trace, lf_span
from app.agents import CoordinatorAgent

async def start_analysis(db: Session, project: Project, zip_path: Optional[str] = None):
    db.add(Event(project_id=project.id, stage="start", message="Analysis requested"))
    db.commit()

    extract_dir = os.path.join(settings.EXTRACT_DIR, f"project_{project.id}")
    os.makedirs(extract_dir, exist_ok=True)

    with lf_trace(name="orchestrator.run", user_id=str(project.owner_id), metadata={"project_id": project.id}) as trace:
        # INGEST
        with lf_span(trace, "ingest"):
            project.status = ProjectStatus.ingesting
            db.add(project); db.commit()
            await progress_bus.emit(project.id, {"type":"stage","stage":"ingest","progress":5,"message":"Starting ingest..."})
            if zip_path and os.path.exists(zip_path):
                with open(zip_path, "rb") as f:
                    zip_bytes = f.read()
                try:
                    total, code = validate_and_extract_zip(zip_bytes, extract_dir)
                except ValueError as e:
                    project.status = ProjectStatus.failed
                    db.add(Event(project_id=project.id, level="error", stage="ingest", message=str(e)))
                    db.add(project); db.commit()
                    await progress_bus.emit(project.id, {"type":"error","stage":"ingest","message":str(e)})
                    return
                db.add(Event(project_id=project.id, stage="ingest", message=f"Extracted {total} files; {code} code files"))
                db.commit()
            else:
                db.add(Event(project_id=project.id, stage="ingest", message="No ZIP provided; repo_url flow not yet implemented"))
                db.commit()

        # DETECT + PREPROCESS (now via agents)
        with lf_span(trace, "agents"):
            project.status = ProjectStatus.preprocessing
            db.add(project); db.commit()
            await progress_bus.emit(project.id, {"type":"stage","stage":"detect","progress":20,"message":"Running RepoDetector & ConfigParser..."})
            await asyncio.sleep(0.3)

            coord = CoordinatorAgent(trace, config={"personas": project.personas, "project_id": project.id})
            results = await coord.run(db, project.id, extract_dir)

            db.add(Event(project_id=project.id, stage="agents", message="Agents completed", payload=results))
            db.commit()

        # ANALYZE (placeholder)
        with lf_span(trace, "analyze"):
            project.status = ProjectStatus.analyzing
            db.add(project); db.commit()
            await progress_bus.emit(project.id, {"type":"stage","stage":"analyze","progress":85,"message":"Synthesizing findings (stub)..."})
            await asyncio.sleep(0.5)

        # COMPLETE
        with lf_span(trace, "complete"):
            project.status = ProjectStatus.complete
            db.add(project); db.commit()
            await progress_bus.emit(project.id, {"type":"stage","stage":"complete","progress":100,"message":"Done"})
