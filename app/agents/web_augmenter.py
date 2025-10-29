from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.observability.langfuse_client import lf_span

class WebAugmentAgent:
    def __init__(self, trace=None, config: Optional[Dict[str, Any]] = None):
        self.trace = trace
        self.config = config or {}

    async def run(self, db: Session, project_id: int, workdir: str) -> Dict[str, Any]:
        """Return a dict of findings/artifacts. Override in subclass."""
        with lf_span(self.trace, "WebAugmentAgent.run"):
            # TODO: implement real logic
            return {"ok": True, "notes": "stub"}

class WebAugmentAgent(WebAugmentAgent):  # type: ignore[misc]
    async def run(self, db, project_id: int, workdir: str):
        # TODO: integrate web lookups; return example recommendations
        recs = [
            {"topic": "FastAPI async patterns", "source": "docs", "status": "todo"},
            {"topic": "OWASP file upload guidance", "source": "owasp", "status": "todo"}
        ]
        return {"ok": True, "recommendations": recs}
