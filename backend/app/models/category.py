from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from app.core.database import Base
import datetime


class Category(Base):
    """Project categories for organization."""
    
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(7), default="#6366f1")  # Hex color
    icon = Column(String(50), nullable=True)  # Emoji or icon name
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Many-to-many relationship with projects
    projects = relationship("ProjectCategory", back_populates="category")


# Association table for project-category many-to-many
class ProjectCategory(Base):
    """Association table for projects and categories."""
    
    __tablename__ = "project_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    project = relationship("Project", back_populates="project_categories")
    category = relationship("Category", back_populates="projects")


# Add relationship to Project
from app.models.project import Project
Project.categories = relationship("ProjectCategory", back_populates="project")
Project.project_categories = relationship("ProjectCategory", back_populates="project")
