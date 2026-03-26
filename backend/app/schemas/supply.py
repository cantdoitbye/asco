from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


class WarehouseBase(BaseModel):
    code: str
    name: str
    district_id: int
    address: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    capacity_mt: Optional[Decimal] = 0
    manager_name: Optional[str] = None
    manager_phone: Optional[str] = None


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseResponse(WarehouseBase):
    id: int
    current_stock_mt: Decimal
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DeliveryBase(BaseModel):
    warehouse_id: int
    anganwadi_center_id: int
    transport_fleet_id: Optional[int] = None
    scheduled_date: Optional[datetime] = None
    total_weight_kg: Optional[Decimal] = 0
    notes: Optional[str] = None


class DeliveryCreate(DeliveryBase):
    pass


class DeliveryUpdate(BaseModel):
    status: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    delivered_date: Optional[datetime] = None
    notes: Optional[str] = None


class DeliveryResponse(DeliveryBase):
    id: int
    tracking_code: str
    status: str
    delivered_date: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class DeliveryListResponse(BaseModel):
    items: List[DeliveryResponse]
    total: int
    page: int
    page_size: int


class InventoryAdjust(BaseModel):
    item_id: int
    warehouse_id: Optional[int] = None
    anganwadi_center_id: Optional[int] = None
    quantity: Decimal
    adjustment_type: str
    reason: Optional[str] = None


class InventoryResponse(BaseModel):
    id: int
    item_id: int
    warehouse_id: Optional[int]
    anganwadi_center_id: Optional[int]
    quantity: Decimal
    min_threshold: Decimal
    max_threshold: Decimal
    last_updated: datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_anganwadi_centers: int
    total_beneficiaries: int
    total_deliveries: int
    pending_deliveries: int
    active_grievances: int
    avg_trust_score: Decimal
    low_stock_alerts: int
    upcoming_scheduled_deliveries: int


class RecentActivity(BaseModel):
    id: int
    type: str
    description: str
    timestamp: datetime
    entity_type: Optional[str]
    entity_id: Optional[int]
