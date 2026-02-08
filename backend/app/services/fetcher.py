import asyncio
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.project import Project, ReleaseSource as ProjectSource
from app.models.release import Release, ReleaseAsset
from app.services.sources import get_source, Release as SourceRelease


class ReleaseFetcher:
    """Service for fetching releases from various sources."""
    
    def __init__(self):
        self.sources = {}
    
    async def fetch_all(self, db: Session) -> int:
        """Fetch releases for all projects."""
        projects = db.query(Project).all()
        total_fetched = 0
        
        for project in projects:
            try:
                fetched = await self.fetch_project(db, project)
                total_fetched += fetched
            except Exception as e:
                print(f"Error fetching releases for {project.name}: {e}")
                continue
        
        db.commit()
        return total_fetched
    
    async def fetch_project(self, db: Session, project: Project) -> int:
        """Fetch releases for a single project."""
        source = get_source(project.source.value)
        
        # Get external ID
        external_id = project.external_id
        if not external_id:
            external_id = source.normalize_external_id(project.repo_url or "")
        
        # Fetch releases
        releases = await source.fetch_releases(external_id)
        
        # Filter to only new releases
        new_count = 0
        last_release = db.query(Release).filter(
            Release.project_id == project.id
        ).order_by(Release.created_at.desc()).first()
        
        for source_release in releases:
            # Check if release already exists
            existing = db.query(Release).filter(
                Release.project_id == project.id,
                Release.version == source_release.version,
            ).first()
            
            if existing:
                continue
            
            # Create release
            release = Release(
                project_id=project.id,
                version=source_release.version,
                tag_name=source_release.tag_name,
                release_date=source_release.release_date,
                changelog=source_release.changelog,
                changelog_url=source_release.changelog_url,
                draft=source_release.draft,
                prerelease=source_release.prerelease,
            )
            db.add(release)
            db.flush()
            
            # Create asset if available
            if source_release.download_url:
                asset = ReleaseAsset(
                    release_id=release.id,
                    name=f"{project.name}-{source_release.version}",
                    download_url=source_release.download_url,
                    size=source_release.size,
                    content_type=source_release.content_type,
                )
                db.add(asset)
            
            new_count += 1
        
        # Update last checked time
        project.last_checked_at = datetime.utcnow()
        
        return new_count
    
    async def fetch_single(self, project_id: int) -> int:
        """Fetch releases for a single project by ID."""
        db = next(get_db())
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                return 0
            
            return await self.fetch_project(db, project)
        finally:
            db.close()


# Global fetcher instance
fetcher = ReleaseFetcher()


async def schedule_fetch_all():
    """Scheduled task to fetch all releases."""
    db = next(get_db())
    try:
        count = await fetcher.fetch_all(db)
        print(f"Fetched {count} new releases")
    finally:
        db.close()


if __name__ == "__main__":
    # Run fetcher
    asyncio.run(schedule_fetch_all())
