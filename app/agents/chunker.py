from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.observability.langfuse_client import lf_span

class ChunkerAgent:
    def __init__(self, trace=None, config: Optional[Dict[str, Any]] = None):
        self.trace = trace
        self.config = config or {}

    async def run(self, db: Session, project_id: int, workdir: str) -> Dict[str, Any]:
        """Return a dict of findings/artifacts. Override in subclass."""
        with lf_span(self.trace, "ChunkerAgent.run"):
            # TODO: implement real logic
            return {"ok": True, "notes": "stub"}

import os, re

class ChunkerAgent(ChunkerAgent):  # type: ignore[misc]
    async def run(self, db, project_id: int, workdir: str):
        # naive: collect .py/.ts files and split into faux "chunks" by function keyword
        code_sections = 0
        for root, _, files in os.walk(workdir):
            for f in files:
                if f.endswith((".py", ".ts", ".js")):
                    try:
                        text = open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore").read()
                        code_sections += len(re.findall(r"\b(def|function)\b", text))
                    except Exception:
                        pass
        return {"ok": True, "sections": code_sections}
