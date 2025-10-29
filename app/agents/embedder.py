from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.observability.langfuse_client import lf_span

class EmbedderAgent:
    def __init__(self, trace=None, config: Optional[Dict[str, Any]] = None):
        self.trace = trace
        self.config = config or {}

    async def run(self, db: Session, project_id: int, workdir: str) -> Dict[str, Any]:
        """Return a dict of findings/artifacts. Override in subclass."""
        with lf_span(self.trace, "EmbedderAgent.run"):
            # TODO: implement real logic
            return {"ok": True, "notes": "stub"}

class EmbedderAgent(EmbedderAgent):  # type: ignore[misc]
    async def run(self, db, project_id: int, workdir: str):
        # TODO: call embeddings + insert into pgvector in a later milestone
        return {"ok": True, "embedded": 0, "note": "pgvector wiring pending"}
