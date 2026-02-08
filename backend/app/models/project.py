from sqlalchemy import Column, Integer, String, Text, Enum, DateTime
from app.core.database import Base
import datetime
import enum


class ReleaseSource(str, enum.Enum):
    GITHUB = "github"
    GITLAB = "gitlab"
    NPM = "npm"
    PYPI = "pypi"
    DOCKER = "docker"
    CRATES = "crates"
    MAVEN = "maven"


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    source = Column(Enum(ReleaseSource), nullable=False)
    external_id = Column(String(255), nullable=True)
    repo_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    last_checked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
