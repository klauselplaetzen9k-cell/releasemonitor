import httpx
from typing import List, Optional
from datetime import datetime
from app.services.sources.base import Release, ReleaseSource


class npmSource(ReleaseSource):
    """Release source for npm registry."""
    
    BASE_URL = "https://registry.npmjs.org"
    
    def normalize_external_id(self, package_url: str) -> str:
        """Extract package name from npm URL or name."""
        # Handle URLs
        if "npmjs.com/" in package_url or "npmjs.org/" in package_url:
            parts = package_url.split("npmjs.com/")[-1].split("npmjs.org/")[-1].rstrip("/")
            # Remove /package suffix
            if parts.endswith("/package"):
                parts = parts[:-8]
            return parts
        # Return as-is if it's just a package name
        return package_url.strip("/")
    
    async def fetch_releases(self, package_name: str) -> List[Release]:
        """Fetch all versions from npm registry."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/{package_name}",
                params={"per_page": 100},
            )
            response.raise_for_status()
            
            data = response.json()
            
            versions = data.get("versions", {})
            time_data = data.get("time", {})
            
            releases = []
            for version, version_data in versions.items():
                release_date_str = time_data.get(version)
                release_date = None
                
                if release_date_str:
                    try:
                        release_date = datetime.fromisoformat(release_date_str.replace("Z", "+00:00"))
                    except ValueError:
                        pass
                
                # Try to get changelog from repository
                repository = version_data.get("repository") or data.get("repository")
                changelog_url = None
                
                if isinstance(repository, dict):
                    repo_url = repository.get("url", "")
                    changelog_url = f"{repo_url}/releases/tag/{version}" if repo_url else None
                elif isinstance(repository, str):
                    changelog_url = f"{repository}/releases/tag/{version}" if repository else None
                
                releases.append(Release(
                    project_id=0,
                    version=version,
                    release_date=release_date,
                    changelog=None,  # npm doesn't provide changelog in registry
                    changelog_url=changelog_url,
                    prerelease=version.startswith(("alpha", "beta", "rc", "-")),
                ))
            
            return releases
    
    async def get_latest_release(self, package_name: str) -> Optional[Release]:
        """Fetch only the latest version from npm registry."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/{package_name}/latest",
            )
            response.raise_for_status()
            
            data = response.json()
            version = data.get("version", "")
            
            return Release(
                project_id=0,
                version=version,
                prerelease=version.startswith(("alpha", "beta", "rc", "-")),
            )
