from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project
from app.services.fetcher import fetcher

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/fetch/{project_id}")
async def trigger_fetch(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually trigger release fetch for a project."""
    # Only allow admins (in production, check user role)
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        new_count = await fetcher.fetch_single(project_id)
        db.commit()
        
        return {
            "message": "Fetch completed",
            "project_id": project_id,
            "new_releases": new_count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fetch failed: {str(e)}")


@router.post("/fetch-all")
async def trigger_fetch_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger release fetch for all projects."""
    try:
        new_count = await fetcher.fetch_all(db)
        
        return {
            "message": "Fetch completed",
            "total_new_releases": new_count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fetch failed: {str(e)}")
