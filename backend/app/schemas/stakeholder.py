from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from ..models import StakeholderType, TrustZone


class StakeholderBase(BaseModel):
    name: str
    type: StakeholderType
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    district_id: Optional[int] = None
    block_id: Optional[int] = None


class StakeholderCreate(StakeholderBase):
    pass


class StakeholderUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[StakeholderType] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    district_id: Optional[int] = None
    block_id: Optional[int] = None
    is_active: Optional[bool] = None


class TrustScoreResponse(BaseModel):
    id: int
    stakeholder_id: int
    score: Decimal
    zone: TrustZone
    delivery_performance: Decimal
    quality_compliance: Decimal
    grievance_rate: Decimal
    data_accuracy: Decimal
    calculated_at: datetime

    class Config:
        from_attributes = True


class StakeholderResponse(StakeholderBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    trust_scores: Optional[List[TrustScoreResponse]] = None

    class Config:
        from_attributes = True


class StakeholderListResponse(BaseModel):
    items: List[StakeholderResponse]
    total: int
    page: int
    page_size: int
