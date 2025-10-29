
from typing import Dict
from sqlalchemy.orm import Session
from ..models import QaLog
from .embedding import search_chunks
from .llm_client import llm_client
import json

PROMPT_SYSTEM = "You are an expert software doc assistant. Answer using the provided code context with file:line references. If unsure, say so."

async def answer_question(db: Session, project_id: int, question: str, persona: str = "SDE") -> Dict:
    hits = await search_chunks(db, project_id, question, top_k=8)
    context_blocks = []
    sources = []
    for r, score in hits:
        snippet = (r.summary or "")[:1200]
        context_blocks.append(f"FILE: {r.path}:{r.start_line}-{r.end_line}\n{snippet}")
        sources.append({"path": r.path, "range": [r.start_line, r.end_line], "score": round(score,3)})
    context = "\n\n".join(context_blocks) if context_blocks else "No code context found."
    messages = [
        {"role": "system", "content": PROMPT_SYSTEM + f" Persona: {persona}."},
        {"role": "user", "content": f"Question: {question}\n\nContext:\n{context}"}
    ]
    answer = await llm_client.chat(messages, temperature=0.2)
    log = QaLog(project_id=project_id, persona=persona, question=question, answer_md=answer, sources_json=json.dumps(sources))
    db.add(log); db.commit()
    return {"markdown": answer, "sources": sources}
