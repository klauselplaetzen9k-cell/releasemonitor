from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.team import Team, TeamMember, TeamProject
from pydantic import BaseModel
import secrets

router = APIRouter(prefix="/teams", tags=["teams"])


class TeamCreate(BaseModel):
    name: str
    description: str = None


class TeamUpdate(BaseModel):
    name: str = None
    description: str = None
    avatar_url: str = None
    is_active: bool = None


class TeamResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str = None
    avatar_url: str = None
    is_active: bool
    member_count: int = 0
    project_count: int = 0
    
    class Config:
        from_attributes = True


class TeamMemberResponse(BaseModel):
    id: int
    user_id: int
    role: str
    joined_at: str
    
    class Config:
        from_attributes = True


def slugify(text: str) -> str:
    """Create URL-friendly slug."""
    import re
    slug = text.lower().replace(" ", "-").replace("_", "-")
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    return slug


@router.get("/", response_model=List[TeamResponse])
def list_teams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List teams the current user belongs to."""
    memberships = db.query(TeamMember).filter(
        TeamMember.user_id == current_user.id,
        TeamMember.is_active == True
    ).all()
    
    result = []
    for membership in memberships:
        team = membership.team
        
        member_count = db.query(TeamMember).filter(
            TeamMember.team_id == team.id,
            TeamMember.is_active == True
        ).count()
        
        project_count = db.query(TeamProject).filter(
            TeamProject.team_id == team.id
        ).count()
        
        result.append({
            **team.__dict__,
            "member_count": member_count,
            "project_count": project_count
        })
    
    return result


@router.post("/", response_model=TeamResponse, status_code=201)
def create_team(
    data: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new team (user becomes owner)."""
    slug = slugify(data.name)
    
    # Check if slug exists
    existing = db.query(Team).filter(Team.slug == slug).first()
    if existing:
        slug = f"{slug}-{secrets.token_hex(4)}"
    
    team = Team(
        name=data.name,
        slug=slug,
        description=data.description,
    )
    db.add(team)
    db.flush()
    
    # Add creator as owner
    owner = TeamMember(
        team_id=team.id,
        user_id=current_user.id,
        role="owner",
    )
    db.add(owner)
    
    db.commit()
    db.refresh(team)
    
    return {**team.__dict__, "member_count": 1, "project_count": 0}


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get team details."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check membership
    membership = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id,
        TeamMember.is_active == True
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this team")
    
    member_count = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.is_active == True
    ).count()
    
    project_count = db.query(TeamProject).filter(
        TeamProject.team_id == team_id
    ).count()
    
    return {**team.__dict__, "member_count": member_count, "project_count": project_count}


@router.post("/{team_id}/members", status_code=201)
def add_team_member(
    team_id: int,
    email: str,
    role: str = "member",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a member to the team (by email)."""
    # Check if current user is owner/admin
    membership = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id,
        TeamMember.role.in_(["owner", "admin"]),
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Only owners/admins can add members")
    
    # Find user by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already a member
    existing = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User is already a member")
    
    new_member = TeamMember(
        team_id=team_id,
        user_id=user.id,
        role=role,
    )
    db.add(new_member)
    db.commit()
    
    return {"message": "Member added"}


@router.delete("/{team_id}/members/{user_id}", status_code=204)
def remove_team_member(
    team_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a member from the team."""
    # Can't remove owner
    # Check permissions
    membership = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id,
        TeamMember.role.in_(["owner", "admin"]),
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Only owners/admins can remove members")
    
    # Find and remove
    to_remove = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user_id,
    ).first()
    
    if not to_remove:
        raise HTTPException(status_code=404, detail="Member not found")
    
    if to_remove.role == "owner":
        raise HTTPException(status_code=400, detail="Cannot remove team owner")
    
    db.delete(to_remove)
    db.commit()


@router.post("/{team_id}/projects/{project_id}", status_code=201)
def add_project_to_team(
    team_id: int,
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a project to the team."""
    # Check membership
    membership = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id,
        TeamMember.role.in_(["owner", "admin", "member"]),
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Must be a team member to add projects")
    
    from app.models.project import Project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if already linked
    existing = db.query(TeamProject).filter(
        TeamProject.team_id == team_id,
        TeamProject.project_id == project_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Project already in team")
    
    link = TeamProject(team_id=team_id, project_id=project_id)
    db.add(link)
    db.commit()
    
    return {"message": "Project added to team"}
