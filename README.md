
# Multi-Agent Code Analysis & Documentation — LLM Build

**Includes:**
- Real LLM integration (Azure OpenAI or OpenAI fallback)
- Chunking + embeddings stored as JSON arrays in DB
- RAG Q&A endpoint with inline file:line citations
- Agents coordinator that ingests repo, chunks, embeds, and produces SDE/PM docs (with Mermaid diagrams)
- Frontend with Git URL, ZIP upload, depth/verbosity, WS progress, Mermaid render

## Run
```bash
docker compose up --build
```
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/docs

## Configure LLM
Set **either** Azure or OpenAI env vars in `docker-compose.yml` (or `.env`):
- Azure: `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`
- OpenAI: `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_EMBED_MODEL`

If no keys are provided, the pipeline runs and produces placeholder summaries, and Q&A will raise an error.

## Flow
1. Sign up / Log in
2. Create a project (Git URL or ZIP)
3. Start Agents → pipeline runs → artifacts created
4. View artifacts (Mermaid diagrams render in UI)
5. Use `/agents/ask` for persona-aware Q&A
