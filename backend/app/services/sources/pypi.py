import httpx
from typing import List, Optional
from datetime import datetime
from app.services.sources.base import Release, ReleaseSource


class PyPISource(ReleaseSource):
    """Release source for PyPI packages."""
    
    BASE_URL = "https://pypi.org/pypi"
    
    def normalize_external_id(self, package_url: str) -> str:
        """Extract package name from PyPI URL or name."""
        # Handle URLs
        if "pypi.org/" in package_url or "pypi.io/" in package_url:
            parts = package_url.split("pypi.org/")[-1].split("pypi.io/")[-1].rstrip("/")
            # Handle /project/ or /simple/ prefixes
            if "/project/" in parts:
                parts = parts.split("/project/")[-1]
            elif "/simple/" in parts:
                parts = parts.split("/simple/")[-1]
            return parts.strip("/")
        return package_url.strip().lower()
    
    async def fetch_releases(self, package_name: str) -> List[Release]:
        """Fetch all versions from PyPI."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/{package_name}/json",
            )
            
            # If package doesn't exist on PyPI, return empty list
            if response.status_code == 404:
                return []
            
            response.raise_for_status()
            
            data = response.json()
            releases_data = data.get("releases", {})
            
            releases = []
            for version, files in releases_data.items():
                release_date = None
                changelog_url = None
                
                # Get upload time from first file
                if files:
                    upload_time = files[0].get("upload_time")
                    if upload_time:
                        try:
                            release_date = datetime.fromisoformat(upload_time.replace("Z", "+00:00"))
                        except ValueError:
                            pass
                
                releases.append(Release(
                    project_id=0,
                    version=version,
                    release_date=release_date,
                    changelog=None,  # PyPI doesn't provide changelog
                    prerelease=version.lower().startswith(("a", "b", "rc", "dev", "alpha", "beta")),
                ))
            
            return releases
    
    async def get_latest_release(self, package_name: str) -> Optional[Release]:
        """Fetch only the latest version from PyPI."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/{package_name}/json",
            )
            
            if response.status_code == 404:
                return None
            
            response.raise_for_status()
            
            data = response.json()
            info = data.get("info", {})
            version = info.get("version", "")
            
            # Get upload time
            releases = data.get("releases", {})
            files = releases.get(version, [])
            release_date = None
            
            if files:
                upload_time = files[0].get("upload_time")
                if upload_time:
                    try:
                        release_date = datetime.fromisoformat(upload_time.replace("Z", "+00:00"))
                    except ValueError:
                        pass
            
            return Release(
                project_id=0,
                version=version,
                release_date=release_date,
                prerelease=version.lower().startswith(("a", "b", "rc", "dev", "alpha", "beta")),
            )
