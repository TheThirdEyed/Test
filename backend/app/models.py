
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
