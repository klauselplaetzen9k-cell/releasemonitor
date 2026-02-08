from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from app.core.database import Base
import datetime


class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    notify_email = Column(Boolean, default=True)
    notify_webhook = Column(Boolean, default=False)
    webhook_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    project = relationship("Project", back_populates="subscriptions")


# Add relationship to User
from app.models.user import User
User.subscriptions = relationship("Subscription", back_populates="user")

# Add relationship to Project
from app.models.project import Project
Project.subscriptions = relationship("Subscription", back_populates="project")
