from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


class AnganwadiCenterBase(BaseModel):
    code: str
    name: str
    village_id: int
    address: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    aww_name: Optional[str] = None
    aww_phone: Optional[str] = None
    total_beneficiaries: Optional[int] = 0
    children_0_3: Optional[int] = 0
    children_3_6: Optional[int] = 0
    pregnant_women: Optional[int] = 0
    lactating_mothers: Optional[int] = 0


class AnganwadiCenterCreate(AnganwadiCenterBase):
    pass


class AnganwadiCenterUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    aww_name: Optional[str] = None
    aww_phone: Optional[str] = None
    total_beneficiaries: Optional[int] = None
    children_0_3: Optional[int] = None
    children_3_6: Optional[int] = None
    pregnant_women: Optional[int] = None
    lactating_mothers: Optional[int] = None
    is_active: Optional[bool] = None


class InventoryResponse(BaseModel):
    id: int
    item_id: int
    quantity: Decimal
    min_threshold: Decimal
    max_threshold: Decimal
    last_updated: datetime

    class Config:
        from_attributes = True


class AnganwadiCenterResponse(AnganwadiCenterBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    inventory: Optional[List[InventoryResponse]] = None

    class Config:
        from_attributes = True


class AnganwadiCenterListResponse(BaseModel):
    items: List[AnganwadiCenterResponse]
    total: int
    page: int
    page_size: int


class DistrictResponse(BaseModel):
    id: int
    name: str
    code: str
    state: str
    created_at: datetime

    class Config:
        from_attributes = True


class BlockResponse(BaseModel):
    id: int
    name: str
    code: str
    district_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class VillageResponse(BaseModel):
    id: int
    name: str
    code: str
    block_id: int
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]
    population: int
    created_at: datetime

    class Config:
        from_attributes = True
