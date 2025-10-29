from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.observability.langfuse_client import lf_span

class PMFeatureAgent:
    def __init__(self, trace=None, config: Optional[Dict[str, Any]] = None):
        self.trace = trace
        self.config = config or {}

    async def run(self, db: Session, project_id: int, workdir: str) -> Dict[str, Any]:
        """Return a dict of findings/artifacts. Override in subclass."""
        with lf_span(self.trace, "PMFeatureAgent.run"):
            # TODO: implement real logic
            return {"ok": True, "notes": "stub"}

import os, re

class PMFeatureAgent(PMFeatureAgent):  # type: ignore[misc]
    async def run(self, db, project_id: int, workdir: str):
        # naive: look for keywords that indicate business features
        keywords = ("payment", "auth", "order", "user", "report", "analytics", "notification")
        found = set()
        for root, _, files in os.walk(workdir):
            for f in files:
                if f.endswith((".py", ".ts", ".js", ".md")):
                    try:
                        text = open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore").read().lower()
                        for kw in keywords:
                            if kw in text:
                                found.add(kw)
                    except Exception:
                        pass
        return {"ok": True, "features": sorted(found)}
