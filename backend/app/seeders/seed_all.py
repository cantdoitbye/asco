"""
Database seeders for populating initial data
"""
import asyncio
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import (
    Base, User, District, Block, Village, AnganwadiCenter,
    Warehouse, Supplier, Inventory, Delivery, Grievance, TrustScore
)
from app.services.auth import get_password_hash
from datetime import datetime, timedelta
import random
import string


def random_string(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def seed_districts(db: Session):
    districts = [
        {"name": "Hyderabad", "state": "Telangana", "code": "HYD"},
        {"name": "Ranga Reddy", "state": "Telangana", "code": "RR"},
        {"name": "Medak", "state": "Telangana", "code": "MDK"},
        {"name": "Warangal", "state": "Telangana", "code": "WGL"},
    ]
    
    for d in districts:
        existing = db.query(District).filter(District.code == d["code"]).first()
        if not existing:
            district = District(**d)
            db.add(district)
    
    db.commit()
    return db.query(District).all()


def seed_blocks(db: Session, districts):
    blocks_data = [
        {"name": "Block A", "code": "BLK-A"},
        {"name": "Block B", "code": "BLK-B"},
        {"name": "Block C", "code": "BLK-C"},
    ]
    
    for district in districts:
        for bd in blocks_data:
            target_code = f"{district.code}-{bd['code']}"
            existing = db.query(Block).filter(
                Block.code == target_code,
                Block.district_id == district.id
            ).first()
            if not existing:
                block = Block(
                    name=f"{district.name} {bd['name']}",
                    code=target_code,
                    district_id=district.id
                )
                db.add(block)
    
    db.commit()
    return db.query(Block).all()


def seed_villages(db: Session, blocks):
    villages = []
    for block in blocks:
        for i in range(1, 4):
            target_name = f"Village {i} - {block.name}"
            existing = db.query(Village).filter(
                Village.block_id == block.id,
                Village.name == target_name
            ).first()
            if not existing:
                village = Village(
                    name=target_name,
                    code=f"{block.code}-V{i}",
                    block_id=block.id
                )
                db.add(village)
    
    db.commit()
    return db.query(Village).all()


def seed_anganwadi_centers(db: Session, villages):
    centers = []
    for village in villages:
        for i in range(1, 3):
                target_name = f"Anganwadi Center {i} - {village.name}"
                existing = db.query(AnganwadiCenter).filter(
                    AnganwadiCenter.name == target_name,
                    AnganwadiCenter.village_id == village.id
                ).first()
                if not existing:
                    code = f"AWC-{random_string(6)}"
                    center = AnganwadiCenter(
                        code=code,
                        name=target_name,
                        village_id=village.id,
                        address=f"Address {i}, {village.name}",
                        latitude=17.3 + random.uniform(-0.5, 0.5),
                        longitude=78.4 + random.uniform(-0.5, 0.5),
                        aww_name=f"Worker {random_string(4)}",
                        aww_phone=f"+91{random.randint(7000000000, 9999999999)}",
                        total_beneficiaries=random.randint(50, 150),
                        children_0_3=random.randint(15, 40),
                        children_3_6=random.randint(20, 50),
                        pregnant_women=random.randint(5, 20),
                        lactating_mothers=random.randint(5, 15),
                        is_active=True
                    )
                    db.add(center)
                    centers.append(center)
                else:
                    centers.append(existing)
    
    db.commit()
    return centers


def seed_warehouses(db: Session, districts):
    warehouses = []
    for district in districts:
        existing = db.query(Warehouse).filter(
            Warehouse.district_id == district.id
        ).first()
        if not existing:
            warehouse = Warehouse(
                name=f"Warehouse - {district.name}",
                code=f"WH-{district.code}",
                district_id=district.id,
                address=f"Industrial Area, {district.name}",
                capacity_mt=1000,
                is_active=True
            )
            db.add(warehouse)
            warehouses.append(warehouse)
    
    db.commit()
    return warehouses


def seed_suppliers(db: Session):
    suppliers_data = [
        {"name": "ABC Traders", "code": "SUP-001"},
        {"name": "XYZ Foods", "code": "SUP-002"},
        {"name": "Quality Supplies", "code": "SUP-003"},
        {"name": "Health Foods India", "code": "SUP-004"},
    ]
    
    suppliers = []
    for sd in suppliers_data:
        existing = db.query(Supplier).filter(Supplier.code == sd["code"]).first()
        if not existing:
            supplier = Supplier(
                name=sd["name"],
                code=sd["code"],
                contact_person=f"Contact {random_string(4)}",
                phone=f"+91{random.randint(7000000000, 9999999999)}",
                email=f"contact@{sd['name'].lower().replace(' ', '')}.com",
                address=f"Business Park, {sd['name']}",
                is_active=True
            )
            db.add(supplier)
            suppliers.append(supplier)
    
    db.commit()
    return suppliers


def seed_users(db: Session):
    users_data = [
        {"email": "admin@asco.gov", "full_name": "System Administrator", "role": UserRole.STATE_ADMIN},
        {"email": "dpo@asco.gov", "full_name": "District Program Officer", "role": UserRole.DISTRICT_ADMIN},
        {"email": "supervisor@asco.gov", "full_name": "Block Supervisor", "role": UserRole.BLOCK_SUPERVISOR},
        {"email": "aww@asco.gov", "full_name": "Anganwadi Worker", "role": UserRole.AWW},
    ]
    
    for ud in users_data:
        existing = db.query(User).filter(User.email == ud["email"]).first()
        if not existing:
            user = User(
                email=ud["email"],
                hashed_password=get_password_hash("password123"),
                role=ud["role"],
                full_name=ud["full_name"],
                is_active=True
            )
            db.add(user)
    
    db.commit()
    return db.query(User).all()


def seed_inventory(db: Session, warehouses):
    if not warehouses:
        return
    
    for warehouse in warehouses:
        existing = db.query(Inventory).filter(
            Inventory.warehouse_id == warehouse.id
        ).first()
        if not existing:
            inventory = Inventory(
                item_id=1,
                warehouse_id=warehouse.id,
                quantity=random.uniform(500, 5000),
                min_threshold=100,
                max_threshold=10000
            )
            db.add(inventory)
    
    db.commit()


def seed_deliveries(db: Session, warehouses, centers):
    if not warehouses or not centers:
        return
    
    for i in range(10):
        warehouse = random.choice(warehouses)
        center = random.choice(centers)
        tracking_code = f"DEL-{random_string(8)}"
        existing = db.query(Delivery).filter(
            Delivery.tracking_code == tracking_code
        ).first()
        if not existing:
            delivery = Delivery(
                tracking_code=tracking_code,
                warehouse_id=warehouse.id,
                anganwadi_center_id=center.id,
                status=random.choice(["pending", "in_transit", "delivered"]),
                scheduled_date=datetime.utcnow() + timedelta(days=random.randint(-5, 10)),
                total_weight_kg=random.uniform(100, 500),
            )
            db.add(delivery)
    
    db.commit()


def seed_grievances(db: Session, users):
    if not users:
        return
        
    categories = ["supply_shortage", "delivery_delay", "quality_issue", "staff_behavior", "infrastructure"]
    statuses = ["open", "in_progress", "resolved", "closed"]
    
    for i in range(10):
        user = random.choice(users)
        existing = db.query(Grievance).filter(
            Grievance.ticket_number == f"GRV-{random_string(8)}"
        ).first()
        
        if not existing:
            grievance = Grievance(
                ticket_number=f"GRV-{random_string(8)}",
                submitted_by_id=user.id,
                title=f"Sample Grievance {i+1}",
                description=f"This is a sample grievance description for testing purposes. Issue number {i+1}.",
                category=random.choice(categories),
                status=random.choice(statuses),
                priority=random.choice(["low", "medium", "high"]),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            db.add(grievance)
    
    db.commit()


def seed_trust_scores(db: Session, users):
    # Trust scores require a stakeholder_id, skip if no stakeholders exist
    pass


def seed_all():
    print("Starting database seeding...")
    
    db = SessionLocal()
    
    try:
        print("Seeding districts...")
        districts = seed_districts(db)
        print(f"  Created {len(districts)} districts")
        
        print("Seeding blocks...")
        blocks = seed_blocks(db, districts)
        print(f"  Created {len(blocks)} blocks")
        
        print("Seeding villages...")
        villages = seed_villages(db, blocks)
        print(f"  Created {len(villages)} villages")
        
        print("Seeding anganwadi centers...")
        centers = seed_anganwadi_centers(db, villages)
        print(f"  Created {len(centers)} anganwadi centers")
        
        print("Seeding warehouses...")
        warehouses = seed_warehouses(db, districts)
        print(f"  Created {len(warehouses)} warehouses")
        
        print("Seeding suppliers...")
        suppliers = seed_suppliers(db)
        print(f"  Created {len(suppliers)} suppliers")
        
        print("Seeding users...")
        users = seed_users(db)
        print(f"  Created {len(users)} users")
        
        print("Seeding inventory...")
        seed_inventory(db, warehouses)
        print("  Inventory seeded")
        
        print("Seeding deliveries...")
        seed_deliveries(db, warehouses, centers)
        print("  Deliveries seeded")
        
        print("Seeding grievances...")
        seed_grievances(db, users)
        print("  Grievances seeded")
        
        print("Seeding trust scores...")
        seed_trust_scores(db, suppliers)
        print("  Trust scores seeded")
        
        print("\nDatabase seeding completed successfully!")
        print("\nDefault users created:")
        print("  - admin@asco.gov / password123 (State Admin)")
        print("  - dpo@asco.gov / password123 (District Admin)")
        print("  - supervisor@asco.gov / password123 (Block Supervisor)")
        print("  - aww@asco.gov / password123 (AWW)")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()
