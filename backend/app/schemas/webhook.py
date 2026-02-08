from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


class WebhookBase(BaseModel):
    project_id: int
    webhook_url: HttpUrl
    channel: Optional[str] = None


class WebhookCreate(WebhookBase):
    notify_releases: bool = True
    notify_prereleases: bool = False
    notify_security: bool = True


class WebhookUpdate(BaseModel):
    webhook_url: Optional[HttpUrl] = None
    channel: Optional[str] = None
    notify_releases: Optional[bool] = None
    notify_prereleases: Optional[bool] = None
    notify_security: Optional[bool] = None
    is_active: Optional[bool] = None


class WebhookResponse(WebhookBase):
    id: int
    user_id: int
    webhook_secret: Optional[str] = None
    notify_releases: bool
    notify_prereleases: bool
    notify_security: bool
    is_active: bool
    last_delivery_at: Optional[datetime] = None
    last_status_code: Optional[int] = None
    failure_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
