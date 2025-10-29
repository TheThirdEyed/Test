
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict
import asyncio, json, random

router = APIRouter(prefix="/analysis", tags=["analysis"])

# In-memory analysis states for demo
ANALYSIS_STATE: Dict[int, Dict] = {}

@router.post("/{project_id}/start")
async def start(project_id: int):
    ANALYSIS_STATE[project_id] = {"status": "processing", "progress": 0, "paused": False}
    return {"ok": True, "status": "processing"}

@router.post("/{project_id}/pause")
async def pause(project_id: int):
    st = ANALYSIS_STATE.get(project_id)
    if not st:
        raise HTTPException(status_code=404, detail="Not running")
    st["paused"] = True
    return {"ok": True, "status": "paused"}

@router.post("/{project_id}/resume")
async def resume(project_id: int):
    st = ANALYSIS_STATE.get(project_id)
    if not st:
        raise HTTPException(status_code=404, detail="Not running")
    st["paused"] = False
    return {"ok": True, "status": "processing"}

@router.websocket("/ws/{project_id}")
async def ws_progress(websocket: WebSocket, project_id: int):
    await websocket.accept()
    # Ensure state
    st = ANALYSIS_STATE.setdefault(project_id, {"status": "processing", "progress": 0, "paused": False})
    try:
        while True:
            if st["status"] == "processing" and not st["paused"]:
                st["progress"] = min(100, st["progress"] + random.randint(1, 5))
                stage = "Preprocessing" if st["progress"] < 40 else "Analysis" if st["progress"] < 80 else "Documentation"
                await websocket.send_text(json.dumps({
                    "project_id": project_id,
                    "progress": st["progress"],
                    "stage": stage,
                    "message": f"{stage}: {st['progress']}%"
                }))
                if st["progress"] >= 100:
                    st["status"] = "completed"
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        return
