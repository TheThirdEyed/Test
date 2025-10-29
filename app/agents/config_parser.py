from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.observability.langfuse_client import lf_span

class ConfigParserAgent:
    def __init__(self, trace=None, config: Optional[Dict[str, Any]] = None):
        self.trace = trace
        self.config = config or {}

    async def run(self, db: Session, project_id: int, workdir: str) -> Dict[str, Any]:
        """Return a dict of findings/artifacts. Override in subclass."""
        with lf_span(self.trace, "ConfigParserAgent.run"):
            # TODO: implement real logic
            return {"ok": True, "notes": "stub"}

import json, os

class ConfigParserAgent(ConfigParserAgent):  # type: ignore[misc]
    async def run(self, db, project_id: int, workdir: str):
        findings = {}
        for fname in ("pyproject.toml", "package.json", "requirements.txt"):
            p = os.path.join(workdir, fname)
            if os.path.exists(p):
                try:
                    txt = open(p, "r", encoding="utf-8").read()
                    findings[fname] = txt[:2000]
                except Exception as e:
                    findings[fname] = f"error: {e}"
        return {"ok": True, "configs": findings}
