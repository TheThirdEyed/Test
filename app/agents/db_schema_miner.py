from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.observability.langfuse_client import lf_span

class DBSchemaAgent:
    def __init__(self, trace=None, config: Optional[Dict[str, Any]] = None):
        self.trace = trace
        self.config = config or {}

    async def run(self, db: Session, project_id: int, workdir: str) -> Dict[str, Any]:
        """Return a dict of findings/artifacts. Override in subclass."""
        with lf_span(self.trace, "DBSchemaAgent.run"):
            # TODO: implement real logic
            return {"ok": True, "notes": "stub"}

import os, re

class DBSchemaAgent(DBSchemaAgent):  # type: ignore[misc]
    async def run(self, db, project_id: int, workdir: str):
        # naive: search for SQLAlchemy Table/Column or Prisma schema
        matches = 0
        for root, _, files in os.walk(workdir):
            for f in files:
                if f.endswith((".py", ".sql", ".prisma", ".ts")):
                    try:
                        text = open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore").read()
                        if re.search(r"Column\(", text) or re.search(r"model\s+\w+\s*\{", text):
                            matches += 1
                    except Exception:
                        pass
        return {"ok": True, "db_artifacts": matches}
