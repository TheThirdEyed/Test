from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.observability.langfuse_client import lf_span

class RepoDetectorAgent:
    def __init__(self, trace=None, config: Optional[Dict[str, Any]] = None):
        self.trace = trace
        self.config = config or {}

    async def run(self, db: Session, project_id: int, workdir: str) -> Dict[str, Any]:
        """Return a dict of findings/artifacts. Override in subclass."""
        with lf_span(self.trace, "RepoDetectorAgent.run"):
            # TODO: implement real logic
            return {"ok": True, "notes": "stub"}

import os, glob

class RepoDetectorAgent(RepoDetectorAgent):  # type: ignore[misc]
    async def run(self, db, project_id: int, workdir: str):
        with lf_span(self.trace, "RepoDetectorAgent.detect"):
            files = os.listdir(workdir) if os.path.exists(workdir) else []
            # naive detection
            stack = []
            if os.path.exists(os.path.join(workdir, "pyproject.toml")) or glob.glob(os.path.join(workdir, "**/*.py"), recursive=True):
                stack.append("python")
            if os.path.exists(os.path.join(workdir, "package.json")) or glob.glob(os.path.join(workdir, "**/*.ts"), recursive=True):
                stack.append("node")
            return {"ok": True, "stack": stack, "files": len(files)}
