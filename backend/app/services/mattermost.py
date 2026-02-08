import httpx
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class MattermostEventType(str, Enum):
    RELEASE_PUBLISHED = "release.published"
    PRERELEASE_AVAILABLE = "prerelease.available"
    RELEASE_UPDATED = "release.updated"


class MattermostMessage(BaseModel):
    """Represents a Mattermost webhook message."""
    text: str
    channel: Optional[str] = None
    username: Optional[str] = None
    icon_url: Optional[str] = None
    attachments: Optional[list] = None


class MattermostService:
    """Service for sending notifications to Mattermost via webhooks."""
    
    def __init__(self, webhook_url: Optional[str] = None, channel: str = None, username: str = "Release Monitor"):
        self.webhook_url = webhook_url
        self.default_channel = channel
        self.default_username = username
    
    def update_config(self, webhook_url: str, channel: str = None, username: str = None):
        """Update Mattermost configuration."""
        self.webhook_url = webhook_url
        if channel:
            self.default_channel = channel
        if username:
            self.default_username = username
    
    async def send_message(self, message: MattermostMessage) -> bool:
        """Send a message to Mattermost webhook."""
        if not self.webhook_url:
            return False
        
        payload = message.model_dump(exclude_none=True)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(self.webhook_url, json=payload)
                response.raise_for_status()
                return True
            except Exception as e:
                print(f"Failed to send Mattermost message: {e}")
                return False
    
    def create_release_message(
        self,
        project_name: str,
        version: str,
        release_url: str,
        changelog: str = None,
        prerelease: bool = False,
        project_icon: str = None,
    ) -> MattermostMessage:
        """Create a message for a new release."""
        # Truncate changelog if too long
        if changelog and len(changelog) > 500:
            changelog = changelog[:500] + "..."
        
        # Build attachment for rich formatting
        attachments = []
        if changelog:
            attachments.append({
                "color": "#36a64f" if not prerelease else "#f39c12",
                "title": f"{project_name} v{version}",
                "title_link": release_url,
                "text": changelog or "*No changelog provided*",
                "fields": [
                    {
                        "short": True,
                        "title": "Type",
                        "value": "Pre-release" if prerelease else "Release",
                    },
                    {
                        "short": True,
                        "title": "Published",
                        "value": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
                    },
                ],
                "footer": "Release Monitor",
                "footer_icon": project_icon,
            })
        else:
            attachments.append({
                "color": "#36a64f" if not prerelease else "#f39c12",
                "title": f"{project_name} v{version}",
                "title_link": release_url,
                "fields": [
                    {
                        "short": True,
                        "title": "Type",
                        "value": "Pre-release" if prerelease else "Release",
                    },
                ],
            })
        
        text = f"📦 **{project_name}** has published a new release: **{version}**"
        if prerelease:
            text += " 🚧 *(pre-release)*"
        
        return MattermostMessage(
            text=text,
            channel=self.default_channel,
            username=self.default_username,
            attachments=attachments,
        )
    
    def create_weekly_digest(
        self,
        project_name: str,
        release_count: int,
        top_version: str,
        project_icon: str = None,
    ) -> MattermostMessage:
        """Create a weekly digest message."""
        text = f"📊 **Weekly Release Digest** for **{project_name}**"
        
        attachments = [{
            "color": "#6366f1",
            "title": f"{release_count} new releases this week",
            "fields": [
                {
                    "short": True,
                    "title": "Latest Version",
                    "value": top_version,
                },
                {
                    "short": True,
                    "title": "Week",
                    "value": datetime.utcnow().strftime("%Y-%W"),
                },
            ],
            "footer": "Release Monitor",
            "footer_icon": project_icon,
        }]
        
        return MattermostMessage(
            text=text,
            channel=self.default_channel,
            username=self.default_username,
            attachments=attachments,
        )
    
    async def notify_release(
        self,
        project_name: str,
        version: str,
        release_url: str,
        changelog: str = None,
        prerelease: bool = False,
        project_icon: str = None,
    ) -> bool:
        """Send a release notification."""
        message = self.create_release_message(
            project_name=project_name,
            version=version,
            release_url=release_url,
            changelog=changelog,
            prerelease=prerelease,
            project_icon=project_icon,
        )
        return await self.send_message(message)
    
    async def test_connection(self) -> bool:
        """Test the webhook connection."""
        test_message = MattermostMessage(
            text="✅ **Release Monitor** connected successfully!",
            username=self.default_username,
        )
        return await self.send_message(test_message)


# Global service instance
mattermost_service = MattermostService()


async def notify_release_to_mattermost(
    webhook_url: str,
    channel: str,
    project_name: str,
    version: str,
    release_url: str,
    changelog: str = None,
    prerelease: bool = False,
) -> bool:
    """Convenience function to send release notification."""
    service = MattermostService(webhook_url=webhook_url, channel=channel)
    return await service.notify_release(
        project_name=project_name,
        version=version,
        release_url=release_url,
        changelog=changelog,
        prerelease=prerelease,
    )
