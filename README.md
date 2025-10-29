
# Multi-Agent Code Analysis & Documentation (Demo Foundation)

This repo boots a production-like skeleton for your system:
- **FastAPI backend** with auth, project creation (zip or repo URL), analysis start/pause/resume, and a **WebSocket** for real-time progress.
- **Postgres + pgvector** database.
- **SolidJS (Vite) frontend** with signup/login, project creation, and **pause/resume** controls wired to sockets.
- **Docker Compose** orchestrating all services.

> This is Milestone 1–3 ready (Foundation, Preprocessing hooks, and Real-Time progress simulation). Extend `services/` to integrate LangGraph, Azure OpenAI, and Langfuse in later milestones.

## Run

```bash
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000 (Swagger at `/docs`)
- DB: Postgres on `localhost:5432`

## Frontend Notes
- Environment vars: `VITE_API_BASE`, `VITE_WS_BASE`
- Demo flow:
  1. Sign up or Log in
  2. Create a project
  3. Start analysis -> watch WebSocket progress
  4. Pause / Resume

## Backend Notes
- Upload via `/projects` with `multipart/form-data`:
  - `name`: string
  - `personas`: `SDE,PM`
  - optional `file`: `.zip`
  - optional `repo_url`: Git URL (mutually exclusive with file)
- WebSocket: `/analysis/ws/{project_id}`
- Pause/Resume: `/analysis/{project_id}/pause|resume`

## Extend
- Replace the simulated loop in `routers/analysis.py` with **LangGraph** graph execution.
- Add **Langfuse** tracing around LLM calls.
- Implement intelligent preprocessing under `services/` and `utils/`.
