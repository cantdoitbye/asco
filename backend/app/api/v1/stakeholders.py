from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from ...database import get_db
from ...models import Stakeholder, District, Block
from ...schemas.stakeholder import (
    StakeholderCreate, StakeholderUpdate, StakeholderResponse, StakeholderListResponse
)
from ...services.auth import get_current_user, check_role
from ...models import User, UserRole, StakeholderType, TrustZone

router = APIRouter()


@router.get("", response_model=StakeholderListResponse)
def list_stakeholders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    stakeholder_type: Optional[StakeholderType] = None,
    district_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Stakeholder)
    
    if stakeholder_type:
        query = query.filter(Stakeholder.type == stakeholder_type)
    if district_id:
        query = query.filter(Stakeholder.district_id == district_id)
    if is_active is not None:
        query = query.filter(Stakeholder.is_active == is_active)
    
    total = query.count()
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()
    
    return StakeholderListResponse(
        items=[StakeholderResponse.from_orm(item) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("", response_model=StakeholderResponse, status_code=201)
def create_stakeholder(
    stakeholder_data: StakeholderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_role([UserRole.STATE_ADMIN, UserRole.DISTRICT_ADMIN]))
):
    new_stakeholder = Stakeholder(**stakeholder_data.dict())
    db.add(new_stakeholder)
    db.commit()
    db.refresh(new_stakeholder)
    return new_stakeholder


@router.get("/{stakeholder_id}", response_model=StakeholderResponse)
def get_stakeholder(
    stakeholder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stakeholder = db.query(Stakeholder).filter(Stakeholder.id == stakeholder_id).first()
    if not stakeholder:
        raise HTTPException(status_code=404, detail="Stakeholder not found")
    return stakeholder


@router.put("/{stakeholder_id}", response_model=StakeholderResponse)
def update_stakeholder(
    stakeholder_id: int,
    update_data: StakeholderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_role([UserRole.STATE_ADMIN, UserRole.DISTRICT_ADMIN]))
):
    stakeholder = db.query(Stakeholder).filter(Stakeholder.id == stakeholder_id).first()
    if not stakeholder:
        raise HTTPException(status_code=404, detail="Stakeholder not found")
    
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(stakeholder, field, value)
    
    db.commit()
    db.refresh(stakeholder)
    return stakeholder


@router.delete("/{stakeholder_id}")
def delete_stakeholder(
    stakeholder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_role([UserRole.STATE_ADMIN]))
):
    stakeholder = db.query(Stakeholder).filter(Stakeholder.id == stakeholder_id).first()
    if not stakeholder:
        raise HTTPException(status_code=404, detail="Stakeholder not found")
    
    stakeholder.is_active = False
    db.commit()
    return {"message": "Stakeholder deactivated successfully"}


@router.get("/districts/list")
def list_districts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    districts = db.query(District).all()
    return [{"id": d.id, "name": d.name, "code": d.code} for d in districts]


@router.get("/blocks/list")
def list_blocks(
    district_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Block)
    if district_id:
        query = query.filter(Block.district_id == district_id)
    blocks = query.all()
    return [{"id": b.id, "name": b.name, "code": b.code, "district_id": b.district_id} for b in blocks]
