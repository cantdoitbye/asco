from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from ...database import get_db
from ...models import AnganwadiCenter, Village, Block, District, Inventory, SupplyItem
from ...schemas.anganwadi import (
    AnganwadiCenterCreate, AnganwadiCenterUpdate, AnganwadiCenterResponse, 
    AnganwadiCenterListResponse, DistrictResponse, BlockResponse, VillageResponse
)
from ...services.auth import get_current_user
from ...models import User

router = APIRouter()


@router.get("")
def list_anganwadi_centers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    village_id: Optional[int] = None,
    block_id: Optional[int] = None,
    district_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(AnganwadiCenter)
    
    if village_id:
        query = query.filter(AnganwadiCenter.village_id == village_id)
    if is_active is not None:
        query = query.filter(AnganwadiCenter.is_active == is_active)
    if block_id or district_id:
        query = query.join(Village).join(Block)
        if block_id:
            query = query.filter(Block.id == block_id)
        if district_id:
            query = query.filter(Block.district_id == district_id)
    
    total = query.count()
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()
    
    return {
        "centers": [
            {
                "id": item.id,
                "code": item.code,
                "name": item.name,
                "village_id": item.village_id,
                "address": item.address,
                "latitude": float(item.latitude) if item.latitude else None,
                "longitude": float(item.longitude) if item.longitude else None,
                "aww_name": item.aww_name,
                "aww_phone": item.aww_phone,
                "total_beneficiaries": item.total_beneficiaries or 0,
                "children_0_3": item.children_0_3 or 0,
                "children_3_6": item.children_3_6 or 0,
                "pregnant_women": item.pregnant_women or 0,
                "lactating_mothers": item.lactating_mothers or 0,
                "is_active": item.is_active,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None
            }
            for item in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.post("", response_model=AnganwadiCenterResponse, status_code=201)
def create_anganwadi_center(
    center_data: AnganwadiCenterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    village = db.query(Village).filter(Village.id == center_data.village_id).first()
    if not village:
        raise HTTPException(status_code=400, detail="Village not found")
    
    existing = db.query(AnganwadiCenter).filter(AnganwadiCenter.code == center_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Center code already exists")
    
    new_center = AnganwadiCenter(**center_data.dict())
    db.add(new_center)
    db.commit()
    db.refresh(new_center)
    return new_center


@router.get("/{center_id}", response_model=AnganwadiCenterResponse)
def get_anganwadi_center(
    center_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    center = db.query(AnganwadiCenter).filter(AnganwadiCenter.id == center_id).first()
    if not center:
        raise HTTPException(status_code=404, detail="Anganwadi center not found")
    return center


@router.put("/{center_id}", response_model=AnganwadiCenterResponse)
def update_anganwadi_center(
    center_id: int,
    update_data: AnganwadiCenterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    center = db.query(AnganwadiCenter).filter(AnganwadiCenter.id == center_id).first()
    if not center:
        raise HTTPException(status_code=404, detail="Anganwadi center not found")
    
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(center, field, value)
    
    db.commit()
    db.refresh(center)
    return center


@router.get("/{center_id}/inventory")
def get_center_inventory(
    center_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    center = db.query(AnganwadiCenter).filter(AnganwadiCenter.id == center_id).first()
    if not center:
        raise HTTPException(status_code=404, detail="Anganwadi center not found")
    
    inventory = db.query(Inventory).filter(Inventory.anganwadi_center_id == center_id).all()
    return {
        "center_id": center_id,
        "center_name": center.name,
        "inventory": [
            {
                "id": inv.id,
                "item_id": inv.item_id,
                "quantity": float(inv.quantity) if inv.quantity else 0,
                "min_threshold": float(inv.min_threshold) if inv.min_threshold else 0,
                "max_threshold": float(inv.max_threshold) if inv.max_threshold else 0,
                "last_updated": inv.last_updated
            }
            for inv in inventory
        ]
    }


@router.get("/geography/districts")
def list_districts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    districts = db.query(District).all()
    return [DistrictResponse.from_orm(d) for d in districts]


@router.get("/geography/blocks")
def list_blocks(
    district_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Block)
    if district_id:
        query = query.filter(Block.district_id == district_id)
    blocks = query.all()
    return [BlockResponse.from_orm(b) for b in blocks]


@router.get("/geography/villages")
def list_villages(
    block_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Village)
    if block_id:
        query = query.filter(Village.block_id == block_id)
    villages = query.all()
    return [VillageResponse.from_orm(v) for v in villages]
