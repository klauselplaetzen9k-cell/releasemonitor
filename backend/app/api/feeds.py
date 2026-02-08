from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.release import Release
from app.models.subscription import Subscription

router = APIRouter(prefix="/feeds", tags=["feeds"])


def generate_rss_feed(
    title: str,
    description: str,
    link: str,
    items: list,
) -> str:
    """Generate RSS 2.0 XML feed."""
    xml_items = ""
    
    for item in items:
        pub_date = ""
        if item.get("published"):
            pub_date = f"<pubDate>{item['published']}</pubDate>"
        
        xml_items += f"""
        <item>
            <title><![CDATA[{item['title']}]]></title>
            <link>{item['link']}</link>
            <guid isPermaLink="true">{item['link']}</guid>
            <description><![CDATA[{item['description']}]]></description>
            {pub_date}
        </item>
"""
    
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
    <channel>
        <title><![CDATA[{title}]]></title>
        <description><![CDATA[{description}]]></description>
        <link>{link}</link>
        <atom:link href="{link}" rel="self" type="application/rss+xml"/>
        <language>en-us</language>
        <lastBuildDate>{datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}</lastBuildDate>
        {xml_items}
    </channel>
</rss>"""
    
    return xml


def generate_atom_feed(
    title: str,
    description: str,
    link: str,
    items: list,
) -> str:
    """Generate Atom 1.0 XML feed."""
    xml_items = ""
    
    for item in items:
        published = ""
        if item.get("published"):
            published = f"<published>{item['published']}</published>"
        
        xml_items += f"""
        <entry>
            <title><![CDATA[{item['title']}]]></title>
            <link href="{item['link']}" rel="alternate"/>
            <id>{item['link']}</id>
            {published}
            <summary type="html"><![CDATA[{item['description']}]]></summary>
        </entry>
"""
    
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title><![CDATA[{title}]]></title>
    <subtitle><![CDATA[{description}]]></subtitle>
    <link href="{link}" rel="self"/>
    <updated>{datetime.utcnow().isoformat() + 'Z'}</updated>
    <id>{link}</id>
    {xml_items}
</feed>"""
    
    return xml


@router.get("/rss")
def get_rss_feed(
    project_id: Optional[int] = None,
    days: int = Query(7, ge=1, le=365),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get releases as RSS 2.0 feed."""
    # Get user's subscribed project IDs if no project specified
    if project_id is None:
        subscriptions = db.query(Subscription.project_id).filter(
            Subscription.user_id == current_user.id
        ).all()
        project_ids = [s[0] for s in subscriptions]
    else:
        project_ids = [project_id]
    
    if not project_ids:
        return "<?xml version='1.0' encoding='UTF-8'?><rss version='2.0'><channel><title>No subscriptions</title></channel></rss>"
    
    # Fetch releases
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    releases = (
        db.query(Release)
        .join(Project)
        .filter(Release.project_id.in_(project_ids))
        .filter(Release.created_at >= cutoff)
        .order_by(Release.created_at.desc())
        .limit(limit)
        .all()
    )
    
    # Build feed items
    items = []
    for release in releases:
        changelog = release.changelog[:200] if release.changelog else ""
        items.append({
            "title": f"{release.project.name} v{release.version}",
            "link": f"https://example.com/projects/{release.project_id}/releases/{release.id}",
            "description": f"New release: {release.version}" + (f"<br/>{changelog}..." if changelog else ""),
            "published": release.created_at.strftime('%a, %d %b %Y %H:%M:%S GMT') if release.created_at else None,
        })
    
    xml = generate_rss_feed(
        title=f"Release Monitor - {project_ids and 'Project Feed' or 'All Releases'}",
        description="Latest releases from your subscribed projects",
        link="https://example.com/feeds/rss",
        items=items,
    )
    
    return Response(content=xml, media_type="application/rss+xml")


@router.get("/atom")
def get_atom_feed(
    project_id: Optional[int] = None,
    days: int = Query(7, ge=1, le=365),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get releases as Atom 1.0 feed."""
    # Get user's subscribed project IDs if no project specified
    if project_id is None:
        subscriptions = db.query(Subscription.project_id).filter(
            Subscription.user_id == current_user.id
        ).all()
        project_ids = [s[0] for s in subscriptions]
    else:
        project_ids = [project_id]
    
    if not project_ids:
        return '<?xml version="1.0" encoding="UTF-8"?><feed xmlns="http://www.w3.org/2005/Atom"><title>No subscriptions</title></feed>'
    
    # Fetch releases
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    releases = (
        db.query(Release)
        .join(Project)
        .filter(Release.project_id.in_(project_ids))
        .filter(Release.created_at >= cutoff)
        .order_by(Release.created_at.desc())
        .limit(limit)
        .all()
    )
    
    # Build feed items
    items = []
    for release in releases:
        changelog = release.changelog[:200] if release.changelog else ""
        items.append({
            "title": f"{release.project.name} v{release.version}",
            "link": f"https://example.com/projects/{release.project_id}/releases/{release.id}",
            "description": f"New release: {release.version}" + (f"<br/>{changelog}..." if changelog else ""),
            "published": release.created_at.isoformat() + "Z" if release.created_at else None,
        })
    
    xml = generate_atom_feed(
        title=f"Release Monitor - {project_ids and 'Project Feed' or 'All Releases'}",
        description="Latest releases from your subscribed projects",
        link="https://example.com/feeds/atom",
        items=items,
    )
    
    return Response(content=xml, media_type="application/atom+xml")


# Import Response for media type
from fastapi import Response
