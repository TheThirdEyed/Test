from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.observability.langfuse_client import lf_span

import os
import re

class APIDocAgent:
    def __init__(self, trace=None, config: Optional[Dict[str, Any]] = None):
        self.trace = trace
        self.config = config or {}

    async def run(self, db: Session, project_id: int, workdir: str) -> Dict[str, Any]:
        with lf_span(self.trace, "APIDocAgent.run"):
            endpoints = []

            # FastAPI-style decorators: @app.get("/path") or @router.post('/path')
            fastapi_pattern = re.compile(
                r'''@(?:app|router)\.(get|post|put|delete|patch)\(\s*["']([^"']+)''',
                re.IGNORECASE
            )

            # Express/Router style: router.get('/path', ...) or app.post("/path", ...)
            express_pattern = re.compile(
                r'''\.(get|post|put|delete|patch)\(\s*["']([^"']+)''',
                re.IGNORECASE
            )

            for root, _, files in os.walk(workdir):
                for f in files:
                    if f.endswith((".py", ".ts", ".js")):
                        p = os.path.join(root, f)
                        try:
                            text = open(p, "r", encoding="utf-8", errors="ignore").read()

                            for m in fastapi_pattern.finditer(text):
                                endpoints.append({
                                    "framework": "fastapi",
                                    "method": m.group(1).upper(),
                                    "path": m.group(2),
                                    "file": p
                                })

                            for m in express_pattern.finditer(text):
                                endpoints.append({
                                    "framework": "express-like",
                                    "method": m.group(1).upper(),
                                    "path": m.group(2),
                                    "file": p
                                })

                        except Exception:
                            # ignore unreadable files
                            pass

            # avoid returning huge payloads
            return {
                "ok": True,
                "endpoints_found": len(endpoints),
                "endpoints": endpoints[:100]
            }
