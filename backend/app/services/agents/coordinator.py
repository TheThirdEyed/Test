
import os, json, asyncio
from sqlalchemy.orm import Session
from ...models import CodeChunk, RepoInfo, DocArtifact
from ..chunker import discover_files, chunk_file
from ..embedding import embed_project_chunks
from ..diagrams import arch_diagram, sequence_auth, data_flow, erd_example
from ..llm_client import llm_client

async def run_pipeline(db: Session, project_id: int, project_path: str, personas: str = "SDE,PM"):
    # 1) Discover & chunk
    files = list(discover_files(project_path))
    total_chunks = 0
    for p in files:
        chunks = chunk_file(p)
        ln = 1
        for ch in chunks:
            row = CodeChunk(project_id=project_id, path=os.path.relpath(p, project_path), start_line=ln, end_line=ln+len(ch.splitlines()), summary=ch[:2000])
            db.add(row)
            total_chunks += 1
            ln += len(ch.splitlines())
    db.commit()

    # 2) Embeddings
    try:
        await embed_project_chunks(db, project_id)
    except Exception as e:
        # Allow running without keys
        pass

    # 3) Summaries via LLM
    try:
        code_count = db.query(CodeChunk).filter(CodeChunk.project_id==project_id).count()
        files_count = len(files)
        prompt = f"Create a concise technical architecture summary for a repo with {files_count} files and {code_count} code chunks. Mention API framework guesses and data flow."
        summary = await llm_client.chat([
            {"role": "system", "content": "You are a precise software architect."},
            {"role": "user", "content": prompt}
        ])
    except Exception:
        summary = "LLM not configured. This is a placeholder summary."

    # 4) Artifacts
    sde_md = f"# Architecture Overview\n\n{summary}\n\n{arch_diagram()}\n\n{sequence_auth()}\n\n{data_flow()}\n\n{erd_example()}"
    db.add(DocArtifact(project_id=project_id, persona="SDE", title="SDE Report", content_md=sde_md))
    pm_md = f"# Feature & Flow Summary\n\nThis report outlines high level capabilities inferred from the repository structure.\n\n{data_flow()}"
    db.add(DocArtifact(project_id=project_id, persona="PM", title="PM Report", content_md=pm_md))
    db.commit()
    return {"files": files_count, "chunks": total_chunks}
