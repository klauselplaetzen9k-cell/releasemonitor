import httpx
from typing import List, Optional
from datetime import datetime
from app.core.config import get_settings
from app.services.sources.base import ReleaseSource, Release
from app.models.project import ReleaseSource as ProjectSource

settings = get_settings()


class GitHubSource(ReleaseSource):
    """Release source for GitHub repositories."""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self):
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if settings.GITHUB_TOKEN:
            self.headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"
    
    def normalize_external_id(self, repo_url: str) -> str:
        """Extract 'owner/repo' from GitHub URL."""
        # Handle various GitHub URL formats
        if "github.com/" in repo_url:
            parts = repo_url.split("github.com/")[1].rstrip("/")
            # Remove trailing .git if present
            if parts.endswith(".git"):
                parts = parts[:-4]
            return parts
        return repo_url
    
    async def fetch_releases(self, external_id: str) -> List[Release]:
        """Fetch all releases from GitHub."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/repos/{external_id}/releases",
                headers=self.headers,
            )
            response.raise_for_status()
            
            releases_data = response.json()
            
            return [self._parse_release(external_id, data) for data in releases_data]
    
    async def get_latest_release(self, external_id: str) -> Optional[Release]:
        """Fetch only the latest release from GitHub."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/repos/{external_id}/releases/latest",
                headers=self.headers,
            )
            
            if response.status_code == 404:
                # No releases, try tags
                return await self._get_latest_tag(external_id, client)
            
            response.raise_for_status()
            data = response.json()
            
            return self._parse_release(external_id, data)
    
    async def _get_latest_tag(self, external_id: str, client: httpx.AsyncClient) -> Optional[Release]:
        """Get latest release from tags if no releases exist."""
        response = await client.get(
            f"{self.BASE_URL}/repos/{external_id}/tags",
            headers=self.headers,
        )
        
        if response.status_code != 200:
            return None
        
        tags = response.json()
        if not tags:
            return None
        
        latest_tag = tags[0]["name"]
        
        # Get commit date for the tag
        response = await client.get(
            f"{self.BASE_URL}/repos/{external_id}/git/refs/tags/{latest_tag}",
            headers=self.headers,
        )
        
        return Release(
            project_id=0,  # Will be set by caller
            version=latest_tag,
            tag_name=latest_tag,
            release_date=datetime.utcnow(),
            prerelease=False,
        )
    
    def _parse_release(self, external_id: str, data: dict) -> Release:
        """Parse GitHub release API response."""
        # Get asset info if available
        download_url = None
        size = None
        content_type = None
        
        if data.get("assets"):
            asset = data["assets"][0]
            download_url = asset.get("browser_download_url")
            size = asset.get("size")
            content_type = asset.get("content_type")
        
        # Get changelog from body
        changelog = data.get("body") or ""
        
        return Release(
            project_id=0,  # Will be set by caller
            version=data.get("tag_name", ""),
            tag_name=data.get("tag_name"),
            release_date=datetime.fromisoformat(data["published_at"].replace("Z", "+00:00")) if data.get("published_at") else None,
            changelog=changelog,
            changelog_url=data.get("html_url"),
            draft=data.get("draft", False),
            prerelease=data.get("prerelease", False),
            download_url=download_url,
            size=size,
            content_type=content_type,
        )
