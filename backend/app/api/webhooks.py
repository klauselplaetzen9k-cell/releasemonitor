import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import HttpUrl
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.webhook import WebhookSubscription
from app.schemas.webhook import WebhookCreate, WebhookResponse, WebhookUpdate

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def generate_secret(length: int = 32) -> str:
    """Generate a secure random secret."""
    return secrets.token_urlsafe(length)


@router.get("/", response_model=List[WebhookResponse])
def list_webhooks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all webhook subscriptions for the current user."""
    webhooks = db.query(WebhookSubscription).filter(
        WebhookSubscription.user_id == current_user.id
    ).all()
    
    return webhooks


@router.post("/", response_model=WebhookResponse, status_code=201)
def create_webhook(
    webhook_data: WebhookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new webhook subscription."""
    # Verify project exists
    project = db.query(Project).filter(Project.id == webhook_data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Generate webhook secret
    secret = generate_secret()
    
    webhook = WebhookSubscription(
        project_id=webhook_data.project_id,
        user_id=current_user.id,
        webhook_url=webhook_data.webhook_url,
        webhook_secret=secret,
        channel=webhook_data.channel,
        notify_releases=webhook_data.notify_releases,
        notify_prereleases=webhook_data.notify_prereleases,
        notify_security=webhook_data.notify_security,
    )
    
    db.add(webhook)
    db.commit()
    db.refresh(webhook)
    
    return webhook


@router.get("/{webhook_id}", response_model=WebhookResponse)
def get_webhook(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific webhook subscription."""
    webhook = db.query(WebhookSubscription).filter(
        WebhookSubscription.id == webhook_id,
        WebhookSubscription.user_id == current_user.id
    ).first()
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    return webhook


@router.put("/{webhook_id}", response_model=WebhookResponse)
def update_webhook(
    webhook_id: int,
    update_data: WebhookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a webhook subscription."""
    webhook = db.query(WebhookSubscription).filter(
        WebhookSubscription.id == webhook_id,
        WebhookSubscription.user_id == current_user.id
    ).first()
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    # Update fields
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(webhook, field, value)
    
    db.commit()
    db.refresh(webhook)
    
    return webhook


@router.delete("/{webhook_id}", status_code=204)
def delete_webhook(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a webhook subscription."""
    webhook = db.query(WebhookSubscription).filter(
        WebhookSubscription.id == webhook_id,
        WebhookSubscription.user_id == current_user.id
    ).first()
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    db.delete(webhook)
    db.commit()


@router.post("/{webhook_id}/test")
async def test_webhook(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a test webhook to verify configuration."""
    from app.services.mattermost import mattermost_service
    
    webhook = db.query(WebhookSubscription).filter(
        WebhookSubscription.id == webhook_id,
        WebhookSubscription.user_id == current_user.id
    ).first()
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    # Test the webhook
    success = await mattermost_service.notify_release(
        webhook_url=webhook.webhook_url,
        channel=webhook.channel,
        project_name="Test Project",
        version="1.0.0",
        release_url="https://example.com",
        changelog="This is a test notification from Release Monitor",
        prerelease=False,
    )
    
    if success:
        webhook.last_delivery_at = datetime.utcnow()
        webhook.last_status_code = 200
        db.commit()
        return {"message": "Test notification sent successfully"}
    else:
        webhook.failure_count += 1
        webhook.last_status_code = 500
        db.commit()
        raise HTTPException(status_code=500, detail="Failed to send test notification")


@router.post("/{webhook_id}/rotate-secret")
def rotate_webhook_secret(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Rotate the webhook secret for security."""
    webhook = db.query(WebhookSubscription).filter(
        WebhookSubscription.id == webhook_id,
        WebhookSubscription.user_id == current_user.id
    ).first()
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    webhook.webhook_secret = generate_secret()
    db.commit()
    
    return {"webhook_secret": webhook.webhook_secret}


# Import datetime for use in test webhook
import datetime
