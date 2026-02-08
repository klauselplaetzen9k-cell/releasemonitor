from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from app.core.database import Base
import datetime


class Team(Base):
    """Team/Workspace for multi-tenant organization."""
    
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    projects = relationship("TeamProject", back_populates="team", cascade="all, delete-orphan")


class TeamMember(Base):
    """Team membership with role-based access."""
    
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(20), default="member")  # owner, admin, member, viewer
    is_active = Column(Boolean, default=True)
    joined_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="team_members")
    
    __table_args__ = (
        # Unique constraint on team_id + user_id
        {"sqlite_autoincrement": True},
    )


class TeamProject(Base):
    """Association of projects to teams."""
    
    __tablename__ = "team_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    team = relationship("Team", back_populates="projects")
    project = relationship("Project", back_populates="team_projects")
    
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )


# Add reverse relationships
from app.models.user import User
User.team_members = relationship("TeamMember", back_populates="user")

from app.models.project import Project
Project.team_projects = relationship("TeamProject", back_populates="project")
