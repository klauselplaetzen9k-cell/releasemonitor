from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.subscription import Subscription
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse, SubscriptionUpdate

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/", response_model=List[SubscriptionResponse])
def list_subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    subscriptions = (
        db.query(Subscription)
        .filter(Subscription.user_id == current_user.id)
        .all()
    )
    
    return [
        {
            **s.__dict__,
            "project_name": s.project.name,
            "project_source": s.project.source.value
        }
        for s in subscriptions
    ]


@router.post("/", response_model=SubscriptionResponse, status_code=201)
def create_subscription(
    sub_data: SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check project exists
    project = db.query(Project).filter(Project.id == sub_data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if already subscribed
    existing = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.project_id == sub_data.project_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already subscribed to this project")
    
    subscription = Subscription(
        user_id=current_user.id,
        **sub_data.model_dump()
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    return {
        **subscription.__dict__,
        "project_name": project.name,
        "project_source": project.source.value
    }


@router.put("/{subscription_id}", response_model=SubscriptionResponse)
def update_subscription(
    subscription_id: int,
    update_data: SubscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(subscription, field, value)
    
    db.commit()
    db.refresh(subscription)
    
    return {
        **subscription.__dict__,
        "project_name": subscription.project.name,
        "project_source": subscription.project.source.value
    }


@router.delete("/{subscription_id}", status_code=204)
def delete_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    db.delete(subscription)
    db.commit()
