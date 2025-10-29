import asyncio
from typing import Dict, Any
from collections import defaultdict

class ProgressBus:
    def __init__(self):
        self.queues = defaultdict(asyncio.Queue)
        self.status: Dict[int, Dict[str, Any]] = {}

    async def emit(self, project_id: int, event: Dict[str, Any]):
        q = self.queues[project_id]
        await q.put(event)
        s = self.status.setdefault(project_id, {"progress": 0, "stage": "created"})
        s.update({k:v for k,v in event.items() if k in ("progress","stage","message","file")})

    def get_queue(self, project_id: int) -> asyncio.Queue:
        return self.queues[project_id]

    def snapshot(self, project_id: int) -> Dict[str, Any]:
        return self.status.get(project_id, {"progress": 0, "stage": "created"})

progress_bus = ProgressBus()
