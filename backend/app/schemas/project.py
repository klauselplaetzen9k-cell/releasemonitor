from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.project import ReleaseSource


class ProjectBase(BaseModel):
    name: str
    source: ReleaseSource
    repo_url: Optional[str] = None
    description: Optional[str] = None
    avatar_url: Optional[str] = None


class ProjectCreate(ProjectBase):
    external_id: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: int
    external_id: Optional[str] = None
    last_checked_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProjectWithReleases(ProjectResponse):
    recent_releases: list = []
    is_subscribed: bool = False
