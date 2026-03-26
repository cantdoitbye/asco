from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import enum


class UserRole(str, enum.Enum):
    STATE_ADMIN = "state_admin"
    DISTRICT_ADMIN = "district_admin"
    BLOCK_SUPERVISOR = "block_supervisor"
    AWW = "aww"
    SUPPLIER = "supplier"
    TRANSPORTER = "transporter"


class StakeholderType(str, enum.Enum):
    SUPPLIER = "supplier"
    TRANSPORT_FLEET = "transport_fleet"
    AWW = "aww"
    CDPO = "cdpo"
    SUPERVISOR = "supervisor"
    COLLECTOR = "collector"
    SECRETARY = "secretary"


class TrustZone(str, enum.Enum):
    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"
    RED = "red"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.AWW)
    is_active = Column(Boolean, default=True)
    stakeholder_id = Column(Integer, ForeignKey("stakeholders.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    stakeholder = relationship("Stakeholder", back_populates="user")


class District(Base):
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    state = Column(String(100), default="Andhra Pradesh")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    blocks = relationship("Block", back_populates="district")


class Block(Base):
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    district = relationship("District", back_populates="blocks")
    villages = relationship("Village", back_populates="block")


class Village(Base):
    __tablename__ = "villages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    block_id = Column(Integer, ForeignKey("blocks.id"), nullable=False)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    population = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    block = relationship("Block", back_populates="villages")
    anganwadi_centers = relationship("AnganwadiCenter", back_populates="village")


class Stakeholder(Base):
    __tablename__ = "stakeholders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(Enum(StakeholderType), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)
    block_id = Column(Integer, ForeignKey("blocks.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="stakeholder")
    trust_scores = relationship("TrustScore", back_populates="stakeholder")


class AnganwadiCenter(Base):
    __tablename__ = "anganwadi_centers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    village_id = Column(Integer, ForeignKey("villages.id"), nullable=False)
    address = Column(Text, nullable=True)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    aww_name = Column(String(255), nullable=True)
    aww_phone = Column(String(20), nullable=True)
    total_beneficiaries = Column(Integer, default=0)
    children_0_3 = Column(Integer, default=0)
    children_3_6 = Column(Integer, default=0)
    pregnant_women = Column(Integer, default=0)
    lactating_mothers = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    village = relationship("Village", back_populates="anganwadi_centers")
    inventory = relationship("Inventory", back_populates="anganwadi_center")


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    address = Column(Text, nullable=True)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    capacity_mt = Column(Numeric(10, 2), default=0)
    current_stock_mt = Column(Numeric(10, 2), default=0)
    manager_name = Column(String(255), nullable=True)
    manager_phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    inventory = relationship("Inventory", back_populates="warehouse")


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    contact_person = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SupplyItem(Base):
    __tablename__ = "supply_items"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    unit = Column(String(50), default="kg")
    unit_price = Column(Numeric(10, 2), default=0)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("supply_items.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    anganwadi_center_id = Column(Integer, ForeignKey("anganwadi_centers.id"), nullable=True)
    quantity = Column(Numeric(10, 2), default=0)
    min_threshold = Column(Numeric(10, 2), default=0)
    max_threshold = Column(Numeric(10, 2), default=0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    warehouse = relationship("Warehouse", back_populates="inventory")
    anganwadi_center = relationship("AnganwadiCenter", back_populates="inventory")


class TransportFleet(Base):
    __tablename__ = "transport_fleets"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_number = Column(String(50), unique=True, nullable=False)
    vehicle_type = Column(String(100), nullable=False)
    driver_name = Column(String(255), nullable=True)
    driver_phone = Column(String(20), nullable=True)
    capacity_kg = Column(Numeric(10, 2), default=0)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    tracking_code = Column(String(50), unique=True, nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    anganwadi_center_id = Column(Integer, ForeignKey("anganwadi_centers.id"), nullable=False)
    transport_fleet_id = Column(Integer, ForeignKey("transport_fleets.id"), nullable=True)
    status = Column(String(50), default="pending")
    scheduled_date = Column(DateTime(timezone=True), nullable=True)
    delivered_date = Column(DateTime(timezone=True), nullable=True)
    total_weight_kg = Column(Numeric(10, 2), default=0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    transport_fleet_id = Column(Integer, ForeignKey("transport_fleets.id"), nullable=True)
    total_distance_km = Column(Numeric(10, 2), default=0)
    estimated_time_minutes = Column(Integer, default=0)
    stops_count = Column(Integer, default=0)
    waypoints = Column(Text, nullable=True)
    is_optimized = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Grievance(Base):
    __tablename__ = "grievances"

    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String(50), unique=True, nullable=False)
    submitted_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String(100), nullable=False)
    priority = Column(String(50), default="medium")
    status = Column(String(50), default="open")
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    ai_analysis = Column(Text, nullable=True)
    sentiment_score = Column(Numeric(3, 2), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TrustScore(Base):
    __tablename__ = "trust_scores"

    id = Column(Integer, primary_key=True, index=True)
    stakeholder_id = Column(Integer, ForeignKey("stakeholders.id"), nullable=False)
    score = Column(Numeric(3, 2), default=0.00)
    zone = Column(Enum(TrustZone), default=TrustZone.YELLOW)
    delivery_performance = Column(Numeric(3, 2), default=0.00)
    quality_compliance = Column(Numeric(3, 2), default=0.00)
    grievance_rate = Column(Numeric(3, 2), default=0.00)
    data_accuracy = Column(Numeric(3, 2), default=0.00)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

    stakeholder = relationship("Stakeholder", back_populates="trust_scores")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
