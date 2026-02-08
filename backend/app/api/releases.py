from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project, ReleaseSource
from app.models.release import Release
from app.schemas.release import ReleaseResponse, ReleaseFeedItem

router = APIRouter(prefix="/releases", tags=["releases"])


@router.get("/", response_model=List[ReleaseFeedItem])
def list_releases(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    project_id: int = None,
    source: ReleaseSource = None,
    days: int = Query(None, ge=1, le=365),
    search: str = None,
    prerelease: bool = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = (
        db.query(Release)
        .join(Project)
        .filter()
    )
    
    if project_id:
        query = query.filter(Release.project_id == project_id)
    
    if source:
        query = query.filter(Project.source == source)
    
    if days:
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = query.filter(Release.created_at >= cutoff)
    
    if prerelease is not None:
        query = query.filter(Release.prerelease == prerelease)
    
    if search:
        query = query.filter(
            (Release.version.ilike(f"%{search}%")) |
            (Project.name.ilike(f"%{search}%"))
        )
    
    releases = (
        query
        .order_by(Release.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return [
        ReleaseFeedItem(
            id=r.id,
            project_name=r.project.name,
            project_source=r.project.source.value,
            project_avatar_url=r.project.avatar_url,
            version=r.version,
            release_date=r.release_date,
            changelog=r.changelog[:200] if r.changelog else None,
            tag_name=r.tag_name,
            prerelease=r.prerelease
        )
        for r in releases
    ]


@router.get("/feed", response_model=List[ReleaseFeedItem])
def get_release_feed(
    limit: int = Query(50, ge=1, le=100),
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get unified release feed for subscribed projects"""
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    from app.models.subscription import Subscription
    
    # Get subscribed project IDs
    subscriptions = db.query(Subscription.project_id).filter(
        Subscription.user_id == current_user.id
    ).all()
    subscribed_ids = [s[0] for s in subscriptions]
    
    if not subscribed_ids:
        return []
    
    releases = (
        db.query(Release)
        .join(Project)
        .filter(Release.project_id.in_(subscribed_ids))
        .filter(Release.created_at >= cutoff)
        .order_by(Release.created_at.desc())
        .limit(limit)
        .all()
    )
    
    return [
        ReleaseFeedItem(
            id=r.id,
            project_name=r.project.name,
            project_source=r.project.source.value,
            project_avatar_url=r.project.avatar_url,
            version=r.version,
            release_date=r.release_date,
            changelog=r.changelog[:200] if r.changelog else None,
            tag_name=r.tag_name,
            prerelease=r.prerelease
        )
        for r in releases
    ]


@router.get("/{release_id}", response_model=ReleaseResponse)
def get_release(
    release_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    release = db.query(Release).filter(Release.id == release_id).first()
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")
    return release


@router.get("/project/{project_id}", response_model=List[ReleaseResponse])
def get_project_releases(
    project_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    releases = (
        db.query(Release)
        .filter(Release.project_id == project_id)
        .order_by(Release.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return releases
