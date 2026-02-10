from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime


class Release(Base):
    __tablename__ = "releases"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    version = Column(String(100), nullable=False)
    release_date = Column(DateTime, nullable=True)
    changelog = Column(Text, nullable=True)
    changelog_url = Column(String(500), nullable=True)
    tag_name = Column(String(255), nullable=True)
    draft = Column(Boolean, default=False)
    prerelease = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationship
    project = relationship("Project", back_populates="releases")
    assets = relationship("ReleaseAsset", back_populates="release")


class ReleaseAsset(Base):
    __tablename__ = "release_assets"
    
    id = Column(Integer, primary_key=True, index=True)
    release_id = Column(Integer, ForeignKey("releases.id"), nullable=False)
    name = Column(String(255), nullable=False)
    download_url = Column(String(500), nullable=True)
    size = Column(Integer, nullable=True)
    content_type = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationship
    release = relationship("Release", back_populates="assets")
