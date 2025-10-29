
import json, math
from typing import List, Tuple
from sqlalchemy.orm import Session
from ..models import CodeChunk
from .llm_client import llm_client

def _cos(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b): return 0.0
    dot = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a)); nb = math.sqrt(sum(y*y for y in b))
    if na == 0 or nb == 0: return 0.0
    return dot/(na*nb)

async def embed_project_chunks(db: Session, project_id: int):
    rows = db.query(CodeChunk).filter(CodeChunk.project_id == project_id).all()
    texts = [ (r.id, (r.summary or "") + "\n" + r.path) for r in rows ]
    if not texts: return 0
    vecs = await llm_client.embed([t for _, t in texts])
    for (cid, _), v in zip(texts, vecs):
        row = db.get(CodeChunk, cid)
        if row:
            row.embedding = json.dumps(v)
    db.commit()
    return len(texts)

async def search_chunks(db: Session, project_id: int, query: str, top_k: int = 8) -> List[Tuple[CodeChunk, float]]:
    q_vec = (await llm_client.embed([query]))[0]
    rows = db.query(CodeChunk).filter(CodeChunk.project_id == project_id).all()
    scored = []
    for r in rows:
        if not r.embedding: continue
        try:
            v = json.loads(r.embedding)
            scored.append((r, _cos(v, q_vec)))
        except Exception:
            pass
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]
