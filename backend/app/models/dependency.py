from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime


class Dependency(Base):
    """Track dependencies for projects."""
    
    __tablename__ = "dependencies"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Dependency info
    name = Column(String(255), nullable=False)
    source = Column(String(50), nullable=False)  # npm, pypi, cargo, maven, etc.
    current_version = Column(String(100), nullable=True)
    latest_version = Column(String(100), nullable=True)
    
    # Tracking settings
    track_updates = Column(Boolean, default=True)
    notify_on_update = Column(Boolean, default=True)
    notify_on_security = Column(Boolean, default=True)
    
    # Timestamps
    last_checked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationship
    project = relationship("Project", back_populates="dependencies")
    
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )


class SecurityAdvisory(Base):
    """Security advisories linked to packages."""
    
    __tablename__ = "security_advisories"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Advisory info
    advisory_id = Column(String(100), unique=True, nullable=False)  # CVE-2024-1234 or GHSA-xxx
    source = Column(String(50), nullable=False)  # github, npm, nvd
    severity = Column(String(20), default="moderate")  # low, moderate, high, critical
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(500), nullable=True)
    
    # Affected version range
    vulnerable_version_range = Column(String(100), nullable=True)
    patched_versions = Column(String(255), nullable=True)
    
    # Timestamps
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class DependencySecurityCheck(Base):
    """Track security checks for dependencies."""
    
    __tablename__ = "dependency_security_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    dependency_id = Column(Integer, ForeignKey("dependencies.id"), nullable=False)
    advisory_id = Column(Integer, ForeignKey("security_advisories.id"), nullable=True)
    
    is_vulnerable = Column(Boolean, default=False)
    check_result = Column(Text, nullable=True)
    checked_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationship
    dependency = relationship("Dependency")
    advisory = relationship("SecurityAdvisory")
