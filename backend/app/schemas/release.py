from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReleaseAssetResponse(BaseModel):
    id: int
    name: str
    download_url: Optional[str] = None
    size: Optional[int] = None
    content_type: Optional[str] = None
    
    class Config:
        from_attributes = True


class ReleaseResponse(BaseModel):
    id: int
    project_id: int
    version: str
    release_date: Optional[datetime] = None
    changelog: Optional[str] = None
    changelog_url: Optional[str] = None
    tag_name: Optional[str] = None
    draft: bool = False
    prerelease: bool = False
    created_at: datetime
    assets: list[ReleaseAssetResponse] = []
    
    class Config:
        from_attributes = True


class ReleaseFeedItem(BaseModel):
    id: int
    project_name: str
    project_source: str
    project_avatar_url: Optional[str] = None
    version: str
    release_date: Optional[datetime] = None
    changelog: Optional[str] = None
    tag_name: Optional[str] = None
    prerelease: bool = False
    
    class Config:
        from_attributes = True
