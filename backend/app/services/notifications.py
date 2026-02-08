from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.project import Project
from app.models.release import Release
from app.models.subscription import Subscription
from app.services.mattermost import mattermost_service


class NotificationService:
    """Service for sending notifications to users via various channels."""
    
    async def notify_new_release(
        self,
        db: Session,
        project: Project,
        release: Release,
    ) -> int:
        """Send notifications for a new release to all subscribers."""
        # Get all active subscriptions for this project
        subscriptions = db.query(Subscription).filter(
            Subscription.project_id == project.id,
        ).all()
        
        notifications_sent = 0
        
        for subscription in subscriptions:
            # Send Mattermost webhook if enabled
            if subscription.notify_webhook and subscription.webhook_url:
                success = await mattermost_service.notify_release(
                    webhook_url=subscription.webhook_url,
                    channel=subscription.webhook_channel or None,
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


# Global service instance
notification_service = NotificationService()


async def process_release_notifications(
    db: Session,
    project: Project,
    release: Release,
) -> int:
    """Process notifications for a newly fetched release."""
    return await notification_service.notify_new_release(db, project, release)
