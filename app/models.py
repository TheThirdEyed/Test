from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, JSON, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

class RoleEnum(str, enum.Enum):
    admin = "admin"
    user = "user"

class ProjectStatus(str, enum.Enum):
    created = "created"
    ingesting = "ingesting"
    preprocessing = "preprocessing"
    analyzing = "analyzing"
    paused = "paused"
    complete = "complete"
    failed = "failed"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.user, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    projects = relationship("Project", back_populates="owner")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=True)
    repo_url = Column(String, nullable=True)
    personas = Column(JSON, default=list)
    config = Column(JSON, default=dict)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.created, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="projects")
    files = relationship("ProjectFile", back_populates="project", cascade="all, delete-orphan")

class ProjectFile(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True, nullable=False)
    path = Column(String, nullable=False)
    mime = Column(String, nullable=True)
    size = Column(Integer, nullable=True)
    is_binary = Column(Boolean, default=False)
    hash = Column(String, nullable=True)
    extracted_to = Column(String, nullable=True)
    error = Column(String, nullable=True)

    project = relationship("Project", back_populates="files")

class EventLevel(str, enum.Enum):
    info = "info"
    warn = "warn"
    error = "error"

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, index=True, nullable=False)
    ts = Column(DateTime(timezone=True), server_default=func.now())
    level = Column(Enum(EventLevel), default=EventLevel.info)
    stage = Column(String, nullable=True)
    message = Column(Text, nullable=False)
    payload = Column(JSON, default=dict)
