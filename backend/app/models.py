
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text
from datetime import datetime, timezone
from .database import Base

def utcnow():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    pw_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="User")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True, nullable=False, default=1)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    repo_source: Mapped[str] = mapped_column(String(10), default="upload")  # upload|git
    repo_url: Mapped[str | None] = mapped_column(String(1024))
    status: Mapped[str] = mapped_column(String(32), default="created")  # created|queued|processing|paused|completed|failed
    personas: Mapped[str] = mapped_column(String(32), default="SDE,PM")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class ActivityEvent(Base):
    __tablename__ = "activity_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), index=True)
    stage: Mapped[str] = mapped_column(String(64))
    message: Mapped[str] = mapped_column(Text)
    level: Mapped[str] = mapped_column(String(16), default="info")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class RepoInfo(Base):
    __tablename__ = "repo_info"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), index=True)
    meta: Mapped[str] = mapped_column(Text)  # JSON string
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class CodeChunk(Base):
    __tablename__ = "code_chunks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), index=True)
    path: Mapped[str] = mapped_column(String(1024))
    kind: Mapped[str] = mapped_column(String(32), default="code")
    start_line: Mapped[int] = mapped_column(Integer, default=0)
    end_line: Mapped[int] = mapped_column(Integer, default=0)
    symbols: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)
    embedding: Mapped[str | None] = mapped_column(Text)  # JSON array for cosine in Python

class AgentRun(Base):
    __tablename__ = "agent_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), index=True)
    status: Mapped[str] = mapped_column(String(16), default="created")  # created|running|paused|completed|failed
    depth: Mapped[str] = mapped_column(String(16), default="standard")
    verbosity: Mapped[str] = mapped_column(String(16), default="standard")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class AgentTask(Base):
    __tablename__ = "agent_tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_run_id: Mapped[int] = mapped_column(Integer, index=True)
    agent_name: Mapped[str] = mapped_column(String(64))
    stage: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(16), default="queued")  # queued|running|done|error
    payload: Mapped[str | None] = mapped_column(Text)
    result: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class DocArtifact(Base):
    __tablename__ = "doc_artifacts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), index=True)
    persona: Mapped[str] = mapped_column(String(16))
    title: Mapped[str] = mapped_column(String(255))
    content_md: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class QaLog(Base):
    __tablename__ = "qa_log"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, index=True)
    persona: Mapped[str] = mapped_column(String(16), default="SDE")
    question: Mapped[str] = mapped_column(Text)
    answer_md: Mapped[str] = mapped_column(Text)
    sources_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
