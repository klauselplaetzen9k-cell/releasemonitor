from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project, ReleaseSource
from app.models.subscription import Subscription
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectWithReleases
from app.services import get_source

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=List[ProjectResponse])
def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    source: Optional[ReleaseSource] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all monitored projects with optional filtering."""
    query = db.query(Project)
    
    if source:
        query = query.filter(Project.source == source)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Project.name.ilike(search_term)) | 
            (Project.description.ilike(search_term))
        )
    
    projects = query.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()
    return projects


@router.get("/search")
def search_projects(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
    source: Optional[ReleaseSource] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Quick search for projects."""
    query = db.query(Project).filter(Project.name.ilike(f"%{q}%"))
    
    if source:
        query = query.filter(Project.source == source)
    
    projects = query.limit(limit).all()
    
    return {
        "query": q,
        "results": [
            {
                "id": p.id,
                "name": p.name,
                "source": p.source.value,
                "description": p.description,
            }
            for p in projects
        ]
    }


@router.get("/{project_id}", response_model=ProjectWithReleases)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get project details with recent releases."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check subscription
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.project_id == project_id
    ).first()
    
    # Get recent releases
    from app.models.release import Release
    recent_releases = (
        db.query(Release)
        .filter(Release.project_id == project_id)
        .order_by(Release.created_at.desc())
        .limit(5)
        .all()
    )
    
    return {
        **project.__dict__,
        "recent_releases": recent_releases,
        "is_subscribed": subscription is not None
    }


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a new project to monitor."""
    # Normalize external ID from repo URL
    if project_data.repo_url and not project_data.external_id:
        source = get_source(project_data.source.value)
        external_id = source.normalize_external_id(project_data.repo_url)
    else:
        external_id = project_data.external_id
    
    # Check if project already exists
    existing = db.query(Project).filter(
        Project.name == project_data.name,
        Project.source == project_data.source
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Project already exists")
    
    project = Project(
        **project_data.model_dump(),
        external_id=external_id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a monitored project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
