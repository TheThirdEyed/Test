# Multi-Agent Code Analysis & Docs — Postgres + Docker + Langfuse + Agents

This package extends the Langfuse scaffold by adding **agent stubs** and
a **Coordinator** that runs them in sequence. It still uses simulated logic for
Milestones 1–3 but is now structured for **Milestone 4 (Agents)**.

## What's new
- `app/agents/` with single-responsibility agent classes:
  - `RepoDetectorAgent`
  - `ConfigParserAgent`
  - `ChunkerAgent`
  - `EmbedderAgent`
  - `APIDocAgent`
  - `DBSchemaAgent`
  - `PMFeatureAgent`
  - `DiagramAgent`
  - `WebAugmentAgent`
  - `CoordinatorAgent`
- Orchestrator now calls the **CoordinatorAgent**, which invokes the above
  agents and emits progress + Langfuse spans per agent.

> This is a production-**ready structure**, but implementations are safe stubs
> you can replace with real logic (AST parsing, embeddings, web search, etc.).

## Quick Start
```bash
cp .env.docker .env
docker compose up --build
```

Open:
- API docs → http://localhost:8000/docs
- Health → http://localhost:8000/healthz

## Next steps
- Plug pgvector + embeddings into `EmbedderAgent`
- Parse API routes for FastAPI/Express/etc. in `APIDocAgent`
- Add real ER extraction in `DBSchemaAgent`
- Generate Mermaid strings in `DiagramAgent`
- Add web lookups in `WebAugmentAgent` and attach source citations
- (Optional) Introduce LangGraph for checkpointed pause/resume
