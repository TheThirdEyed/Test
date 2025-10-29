from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.observability.langfuse_client import lf_span
from .repo_detector import RepoDetectorAgent
from .config_parser import ConfigParserAgent
from .chunker import ChunkerAgent
from .embedder import EmbedderAgent
from .api_extractor import APIDocAgent
from .db_schema_miner import DBSchemaAgent
from .pm_feature_miner import PMFeatureAgent
from .diagrammer import DiagramAgent
from .web_augmenter import WebAugmentAgent

class CoordinatorAgent:
    def __init__(self, trace=None, config: Optional[Dict[str, Any]] = None):
        self.trace = trace
        self.config = config or {}

    async def run(self, db: Session, project_id: int, workdir: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        with lf_span(self.trace, "Coordinator.run", {"project_id": project_id}):
            # sequence (can parallelize later)
            results["repo"] = await RepoDetectorAgent(self.trace, self.config).run(db, project_id, workdir)
            results["config"] = await ConfigParserAgent(self.trace, self.config).run(db, project_id, workdir)
            results["chunking"] = await ChunkerAgent(self.trace, self.config).run(db, project_id, workdir)
            results["embed"] = await EmbedderAgent(self.trace, self.config).run(db, project_id, workdir)
            results["api"] = await APIDocAgent(self.trace, self.config).run(db, project_id, workdir)
            results["db"] = await DBSchemaAgent(self.trace, self.config).run(db, project_id, workdir)
            results["pm"] = await PMFeatureAgent(self.trace, self.config).run(db, project_id, workdir)
            results["diagram"] = await DiagramAgent(self.trace, self.config).run(db, project_id, workdir)
            results["web"] = await WebAugmentAgent(self.trace, self.config).run(db, project_id, workdir)
        return results
