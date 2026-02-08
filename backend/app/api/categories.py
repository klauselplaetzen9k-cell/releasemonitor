from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.category import Category, ProjectCategory
from pydantic import BaseModel

router = APIRouter(prefix="/categories", tags=["categories"])


class CategoryCreate(BaseModel):
    name: str
    description: str = None
    color: str = "#6366f1"
    icon: str = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str = None
    color: str
    icon: str = None
    project_count: int = 0
    
    class Config:
        from_attributes = True


def slugify(text: str) -> str:
    """Create URL-friendly slug."""
    return text.lower().replace(" ", "-").replace("_", "-")


@router.get("/", response_model=List[CategoryResponse])
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all categories with project counts."""
    categories = db.query(Category).all()
    
    result = []
    for cat in categories:
        count = db.query(ProjectCategory).filter(
            ProjectCategory.category_id == cat.id
        ).count()
        
        result.append({
            **cat.__dict__,
            "project_count": count
        })
    
    return result


@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new category."""
    slug = slugify(data.name)
    
    # Check if exists
    existing = db.query(Category).filter(Category.slug == slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    category = Category(
        name=data.name,
        slug=slug,
        description=data.description,
        color=data.color,
        icon=data.icon,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return {**category.__dict__, "project_count": 0}


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a category."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db.delete(category)
    db.commit()


@router.post("/{category_id}/projects/{project_id}", status_code=201)
def add_project_to_category(
    category_id: int,
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a project to a category."""
    # Verify category exists
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Verify project exists
    from app.models.project import Project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if already linked
    existing = db.query(ProjectCategory).filter(
        ProjectCategory.category_id == category_id,
        ProjectCategory.project_id == project_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Project already in category")
    
    link = ProjectCategory(category_id=category_id, project_id=project_id)
    db.add(link)
    db.commit()
    
    return {"message": "Project added to category"}


@router.delete("/{category_id}/projects/{project_id}", status_code=204)
def remove_project_from_category(
    category_id: int,
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a project from a category."""
    link = db.query(ProjectCategory).filter(
        ProjectCategory.category_id == category_id,
        ProjectCategory.project_id == project_id
    ).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    db.delete(link)
    db.commit()
