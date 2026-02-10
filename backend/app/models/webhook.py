from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime


class WebhookSubscription(Base):
    """Webhook subscription for project notifications."""
    
    __tablename__ = "webhook_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Webhook configuration
    webhook_url = Column(String(500), nullable=False)
    webhook_secret = Column(String(255), nullable=True)
    channel = Column(String(100), nullable=True)
    
    # Notification settings
    notify_releases = Column(Boolean, default=True)
    notify_prereleases = Column(Boolean, default=False)
    notify_security = Column(Boolean, default=True)
    
    # Delivery tracking
    is_active = Column(Boolean, default=True)
    last_delivery_at = Column(DateTime, nullable=True)
    last_status_code = Column(Integer, nullable=True)
    failure_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="webhook_subscriptions")
    user = relationship("User", back_populates="webhook_subscriptions")
