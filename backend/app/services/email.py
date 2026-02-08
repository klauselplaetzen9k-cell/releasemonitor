import asyncio
from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session
from jinja2 import Template


@dataclass
class EmailConfig:
    """System-wide SMTP configuration."""
    host: str
    port: int
    username: str
    password: str
    from_email: str = "releases@example.com"
    from_name: str = "Release Monitor"
    use_tls: bool = True


class EmailService:
    """Email notification service with system-wide SMTP config."""
    
    def __init__(self, config: Optional[EmailConfig] = None):
        self.config = config
    
    def is_configured(self) -> bool:
        """Check if email is configured."""
        return self.config is not None and bool(self.config.host)
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> bool:
        """Send an email using SMTP."""
        if not self.is_configured():
            print(f"[EMAIL DISABLED] Would send to {to_email}: {subject}")
            return False
        
        import aiosmtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.config.from_name} <{self.config.from_email}>"
            msg['To'] = to_email
            
            # Add HTML and text parts
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            if text_body:
                msg.attach(MIMEText(text_body, 'plain'))
            
            # Send via SMTP
            await aiosmtplib.send(
                msg,
                hostname=self.config.host,
                port=self.config.port,
                use_tls=self.config.use_tls,
                username=self.config.username,
                password=self.config.password,
            )
            
            return True
            
        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send email: {e}")
            return False
    
    async def send_release_notification(
        self,
        to_email: str,
        project_name: str,
        version: str,
        release_url: str,
        changelog: Optional[str] = None,
        prerelease: bool = False,
    ) -> bool:
        """Send a release notification email."""
        subject = f"📦 New release: {project_name} v{version}"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1f2937; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 30px; border-radius: 12px 12px 0 0; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px;">📦 New Release Published</h1>
            </div>
            
            <div style="background: #f9fafb; padding: 30px; border-radius: 0 0 12px 12px; border: 1px solid #e5e7eb; border-top: none;">
                <p style="font-size: 18px; margin-top: 0;">
                    <strong>{project_name}</strong> v{version} has been released!
                </p>
                
                {"<p style='background: #fef3c7; color: #92400e; padding: 8px 12px; border-radius: 6px; display: inline-block;'>🚧 Pre-release</p>" if prerelease else ""}
                
                <p style="margin: 20px 0;">
                    <a href="{release_url}" style="display: inline-block; background: #6366f1; color: white; text-decoration: none; padding: 12px 24px; border-radius: 8px; font-weight: 600;">View Release</a>
                </p>
                
                {"<div style='margin-top: 20px; padding: 15px; background: white; border-radius: 8px; border: 1px solid #e5e7eb;'><h3 style='margin-top: 0;'>📝 Changelog Preview</h3><pre style='white-space: pre-wrap; font-size: 14px; color: #4b5563;'>" + (changelog[:500] + "..." if changelog and len(changelog) > 500 else changelog or "No changelog provided") + "</pre></div>" if changelog else ""}
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                <p style="color: #6b7280; font-size: 14px; text-align: center;">
                    You're receiving this because you subscribed to releases from {project_name}.<br>
                    <a href="{release_url.replace('/releases/', '/settings/')}" style="color: #6366f1;">Manage notification settings</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_body=html,
        )
    
    async def send_weekly_digest(
        self,
        to_email: str,
        project_name: str,
        release_count: int,
        releases: list,
        digest_url: str,
    ) -> bool:
        """Send a weekly digest email."""
        subject = f"Weekly Digest: {release_count} releases from {project_name}"
        
        releases_html = ""
        for release in releases:
            releases_html += f"""
            <div style="padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                <strong>{release.get('version', 'Unknown')}</strong>
                {"<span style='background: #fef3c7; color: #92400e; padding: 2px 8px; border-radius: 4px; font-size: 12px;'>Pre-release</span>" if release.get('prerelease') else ""}
                <br><small style="color: #6b7280;">{release.get('date', 'No date')}</small>
            </div>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1f2937; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 30px; border-radius: 12px 12px 0 0; text-align: center;">
                <h1 style="color: white; margin: 0;">📊 Weekly Release Digest</h1>
            </div>
            
            <div style="background: #f9fafb; padding: 30px; border-radius: 0 0 12px 12px; border: 1px solid #e5e7eb;">
                <p style="font-size: 18px;">
                    <strong>{project_name}</strong> had <strong>{release_count}</strong> releases this week.
                </p>
                
                <div style="margin: 20px 0;">
                    {releases_html}
                </div>
                
                <p style="margin: 20px 0; text-align: center;">
                    <a href="{digest_url}" style="display: inline-block; background: #6366f1; color: white; text-decoration: none; padding: 12px 24px; border-radius: 8px; font-weight: 600;">View All Releases</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_body=html,
        )


# Global service instance
email_service = EmailService()


# Initialize email service from config
def init_email_service():
    """Initialize email service from environment config."""
    from app.core.config import get_settings
    settings = get_settings()
    
    if settings.SMTP_HOST and settings.SMTP_USER:
        email_service.config = EmailConfig(
            host=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            from_email=settings.SMTP_FROM or "releases@example.com",
        )
        return True
    return False


async def send_notification_email(
    to_email: str,
    project_name: str,
    version: str,
    release_url: str,
    changelog: str = None,
    prerelease: bool = False,
) -> bool:
    """Convenience function to send release notification."""
    return await email_service.send_release_notification(
        to_email=to_email,
        project_name=project_name,
        version=version,
        release_url=release_url,
        changelog=changelog,
        prerelease=prerelease,
    )
