from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal
from ...database import get_db
from ...models import Warehouse, Delivery, Inventory, SupplyItem, AnganwadiCenter, TransportFleet
from ...schemas.supply import (
    WarehouseCreate, WarehouseResponse, DeliveryCreate, DeliveryUpdate,
    DeliveryResponse, DeliveryListResponse, InventoryAdjust, DashboardStats
)
from ...services.auth import get_current_user, check_role
from ...models import User, UserRole

router = APIRouter()


@router.get("/warehouses", response_model=list[WarehouseResponse])
def list_warehouses(
    district_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Warehouse).filter(Warehouse.is_active == True)
    if district_id:
        query = query.filter(Warehouse.district_id == district_id)
    return query.all()


@router.post("/warehouses", response_model=WarehouseResponse, status_code=201)
def create_warehouse(
    warehouse_data: WarehouseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_role([UserRole.STATE_ADMIN, UserRole.DISTRICT_ADMIN]))
):
    new_warehouse = Warehouse(**warehouse_data.dict())
    db.add(new_warehouse)
    db.commit()
    db.refresh(new_warehouse)
    return new_warehouse


@router.get("/deliveries", response_model=DeliveryListResponse)
def list_deliveries(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    warehouse_id: Optional[int] = None,
    anganwadi_center_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Delivery)
    
    if status:
        query = query.filter(Delivery.status == status)
    if warehouse_id:
        query = query.filter(Delivery.warehouse_id == warehouse_id)
    if anganwadi_center_id:
        query = query.filter(Delivery.anganwadi_center_id == anganwadi_center_id)
    
    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(Delivery.created_at.desc()).offset(offset).limit(page_size).all()
    
    return DeliveryListResponse(
        items=[DeliveryResponse.from_orm(item) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/deliveries", response_model=DeliveryResponse, status_code=201)
def create_delivery(
    delivery_data: DeliveryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    import uuid
    tracking_code = f"DEL-{uuid.uuid4().hex[:8].upper()}"
    
    new_delivery = Delivery(
        tracking_code=tracking_code,
        **delivery_data.dict()
    )
    db.add(new_delivery)
    db.commit()
    db.refresh(new_delivery)
    return new_delivery


@router.get("/deliveries/{delivery_id}", response_model=DeliveryResponse)
def get_delivery(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery


@router.patch("/deliveries/{delivery_id}", response_model=DeliveryResponse)
def update_delivery(
    delivery_id: int,
    update_data: DeliveryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(delivery, field, value)
    
    db.commit()
    db.refresh(delivery)
    return delivery


@router.post("/deliveries/{delivery_id}/confirm")
def confirm_delivery(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    
    from datetime import datetime
    delivery.status = "delivered"
    delivery.delivered_date = datetime.utcnow()
    db.commit()
    return {"message": "Delivery confirmed", "tracking_code": delivery.tracking_code}


@router.get("/inventory")
def list_inventory(
    warehouse_id: Optional[int] = None,
    anganwadi_center_id: Optional[int] = None,
    low_stock: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Inventory)
    
    if warehouse_id:
        query = query.filter(Inventory.warehouse_id == warehouse_id)
    if anganwadi_center_id:
        query = query.filter(Inventory.anganwadi_center_id == anganwadi_center_id)
    
    inventory_items = query.all()
    
    if low_stock:
        inventory_items = [
            item for item in inventory_items 
            if item.quantity <= item.min_threshold
        ]
    
    return {
        "items": [
            {
                "id": item.id,
                "item_id": item.item_id,
                "warehouse_id": item.warehouse_id,
                "anganwadi_center_id": item.anganwadi_center_id,
                "quantity": float(item.quantity) if item.quantity else 0,
                "min_threshold": float(item.min_threshold) if item.min_threshold else 0,
                "max_threshold": float(item.max_threshold) if item.max_threshold else 0,
                "last_updated": item.last_updated
            }
            for item in inventory_items
        ]
    }


@router.post("/inventory/adjust")
def adjust_inventory(
    adjust_data: InventoryAdjust,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Inventory).filter(Inventory.item_id == adjust_data.item_id)
    
    if adjust_data.warehouse_id:
        query = query.filter(Inventory.warehouse_id == adjust_data.warehouse_id)
    elif adjust_data.anganwadi_center_id:
        query = query.filter(Inventory.anganwadi_center_id == adjust_data.anganwadi_center_id)
    
    inventory = query.first()
    
    if not inventory:
        inventory = Inventory(
            item_id=adjust_data.item_id,
            warehouse_id=adjust_data.warehouse_id,
            anganwadi_center_id=adjust_data.anganwadi_center_id,
            quantity=Decimal("0")
        )
        db.add(inventory)
    
    if adjust_data.adjustment_type == "add":
        inventory.quantity += adjust_data.quantity
    elif adjust_data.adjustment_type == "subtract":
        inventory.quantity -= adjust_data.quantity
    elif adjust_data.adjustment_type == "set":
        inventory.quantity = adjust_data.quantity
    
    db.commit()
    db.refresh(inventory)
    
    return {
        "message": "Inventory adjusted successfully",
        "new_quantity": float(inventory.quantity)
    }


@router.get("/supply-items")
def list_supply_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    items = db.query(SupplyItem).filter(SupplyItem.is_active == True).all()
    return [
        {
            "id": item.id,
            "code": item.code,
            "name": item.name,
            "category": item.category,
            "unit": item.unit,
            "unit_price": float(item.unit_price) if item.unit_price else 0
        }
        for item in items
    ]
