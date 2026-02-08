from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Release:
    """Represents a software release from any source."""
    project_id: int
    version: str
    tag_name: Optional[str] = None
    release_date: Optional[datetime] = None
    changelog: Optional[str] = None
    changelog_url: Optional[str] = None
    draft: bool = False
    prerelease: bool = False
    download_url: Optional[str] = None
    size: Optional[int] = None
    content_type: Optional[str] = None


class ReleaseSource(ABC):
    """Abstract base class for release sources."""
    
    @abstractmethod
    async def fetch_releases(self, external_id: str) -> List[Release]:
        """Fetch all releases for a project."""
        pass
    
    @abstractmethod
    async def get_latest_release(self, external_id: str) -> Optional[Release]:
        """Fetch the latest release only."""
        pass
    
    @abstractmethod
    def normalize_external_id(self, repo_url: str) -> str:
        """Extract external ID from repository URL."""
        pass
