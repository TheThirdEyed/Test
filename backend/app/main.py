
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import projects, analysis, admin, agents
from .auth import router as auth_router

app = FastAPI(title="Multi-Agent Code Documentation", version="0.3.0")

origins = [o for o in settings.ALLOW_ORIGINS if o != "*"]
use_regex = any(o == "*" for o in settings.ALLOW_ORIGINS)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if not use_regex else [],
    allow_origin_regex=".*" if use_regex else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(projects.router)
app.include_router(analysis.router)
app.include_router(agents.router)
app.include_router(admin.router)
