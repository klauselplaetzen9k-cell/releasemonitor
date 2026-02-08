import asyncio
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.project import Project
from app.models.release import Release
from app.models.subscription import Subscription
from app.services.email import email_service
from app.services.mattermost import mattermost_service


class NotificationService:
    """Service for sending notifications via email and webhooks."""
    
    async def notify_new_release(
        self,
        db: Session,
        project: Project,
        release: Release,
    ) -> int:
        """Send notifications for a new release to all subscribers."""
        # Get all active email subscriptions for this project
        # Note: In a real app, you'd query the user's email preferences
        # For now, we send to configured email if enabled
        
        notifications_sent = 0
        
        # Send email notification if configured
        if email_service.is_configured():
            # In production, you'd fetch subscriber emails from DB
            # For now, we just log that emails would be sent
            print(f"[EMAIL] Would notify subscribers of {project.name} about v{release.version}")
        
        # Send Mattermost webhooks
        webhook_subs = db.query(WebhookSubscription).filter(
            WebhookSubscription.project_id == project.id,
            WebhookSubscription.notify_releases == True,
            WebhookSubscription.is_active == True,
        ).all()
        
        for sub in webhook_subs:
            if sub.webhook_url:
                success = await mattermost_service.notify_release(
                    webhook_url=sub.webhook_url,
                    channel=sub.channel,
                    project_name=project.name,
                    version=release.version,
                    release_url=f"https://example.com/projects/{project.id}/releases/{release.id}",
                    changelog=release.changelog,
                    prerelease=release.prerelease,
                )
                if success:
                    notifications_sent += 1
        
        return notifications_sent
    
    async def notify_release_batch(
        self,
        db: Session,
        project: Project,
        releases: List[Release],
    ) -> int:
        """Send notifications for multiple releases."""
        notifications_sent = 0
        
        for release in releases:
            sent = await self.notify_new_release(db, project, release)
            notifications_sent += sent
        
        return notifications_sent


# Import webhook subscription for notification service
from app.models.webhook import WebhookSubscription

# Global service instance
notification_service = NotificationService()


async def process_release_notifications(
    db: Session,
    project: Project,
    release: Release,
) -> int:
    """Process notifications for a newly fetched release."""
    return await notification_service.notify_new_release(db, project, release)


# Initialize email on module load
# This will be called when the app starts
def setup_notifications():
    """Setup notification services."""
    init_email_service()
