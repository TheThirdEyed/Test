from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.observability.langfuse_client import lf_span

class DiagramAgent:
    def __init__(self, trace=None, config: Optional[Dict[str, Any]] = None):
        self.trace = trace
        self.config = config or {}

    async def run(self, db: Session, project_id: int, workdir: str) -> Dict[str, Any]:
        """Return a dict of findings/artifacts. Override in subclass."""
        with lf_span(self.trace, "DiagramAgent.run"):
            # TODO: implement real logic
            return {"ok": True, "notes": "stub"}

class DiagramAgent(DiagramAgent):  # type: ignore[misc]
    async def run(self, db, project_id: int, workdir: str):
        # placeholder Mermaid
        mermaid = """
```mermaid
flowchart LR
  Client-->API[FastAPI]
  API-->Workers[Agents]
  Workers-->DB[(Postgres + future pgvector)]
  Workers-->Blob[(Object Storage)]
```
"""
        return {"ok": True, "mermaid": mermaid}
