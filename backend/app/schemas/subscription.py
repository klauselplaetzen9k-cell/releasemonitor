from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SubscriptionBase(BaseModel):
    project_id: int
    notify_email: bool = True
    notify_webhook: bool = False
    webhook_url: Optional[str] = None


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionResponse(SubscriptionBase):
    id: int
    user_id: int
    created_at: datetime
    project_name: str
    project_source: str
    
    class Config:
        from_attributes = True


class SubscriptionUpdate(BaseModel):
    notify_email: Optional[bool] = None
    notify_webhook: Optional[bool] = None
    webhook_url: Optional[str] = None
