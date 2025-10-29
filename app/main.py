from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.database import Base, engine
from app.auth import router as auth_router
from app.routers.projects import router as projects_router
from app.routers.admin import router as admin_router
from app.observability.langfuse_client import lf_trace

app = FastAPI(title="Multi-Agent Code Analysis & Docs — API", version="0.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def tracing_middleware(request: Request, call_next):
    with lf_trace(name="http.request", metadata={"path": request.url.path, "method": request.method}):
        response = await call_next(request)
        return response

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(admin_router)

@app.get("/healthz")
def healthz():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"ok": True}
