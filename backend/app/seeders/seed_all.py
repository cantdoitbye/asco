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
                capacity_kg=100000,
                current_utilization=random.uniform(20, 60)
            )
            db.add(warehouse)
            warehouses.append(warehouse)
    
    db.commit()
    return warehouses


def seed_suppliers(db: Session):
    suppliers_data = [
        {"name": "ABC Traders", "code": "SUP-001", "category": "food_grains"},
        {"name": "XYZ Foods", "code": "SUP-002", "category": "dairy"},
        {"name": "Quality Supplies", "code": "SUP-003", "category": "nutrition"},
        {"name": "Health Foods India", "code": "SUP-004", "category": "supplements"},
    ]
    
    suppliers = []
    for sd in suppliers_data:
        existing = db.query(Supplier).filter(Supplier.code == sd["code"]).first()
        if not existing:
            supplier = Supplier(
                name=sd["name"],
                code=sd["code"],
                category=sd["category"],
                contact_person=f"Contact {random_string(4)}",
                phone=f"+91{random.randint(7000000000, 9999999999)}",
                email=f"contact@{sd['name'].lower().replace(' ', '')}.com",
                address=f"Business Park, {sd['name']}",
                quality_rating=random.uniform(3.5, 4.8),
                is_active=True
            )
            db.add(supplier)
            suppliers.append(supplier)
    
    db.commit()
    return suppliers


def seed_users(db: Session):
    users_data = [
        {"email": "admin@asco.gov", "username": "admin", "role": "admin", "full_name": "System Administrator"},
        {"email": "dpo@asco.gov", "username": "dpo_hyd", "role": "district_program_officer", "full_name": "District Program Officer"},
        {"email": "manager@asco.gov", "username": "manager", "role": "supply_chain_manager", "full_name": "Supply Chain Manager"},
        {"email": "viewer@asco.gov", "username": "viewer", "role": "viewer", "full_name": "Report Viewer"},
    ]
    
    for ud in users_data:
        existing = db.query(User).filter(User.email == ud["email"]).first()
        if not existing:
            user = User(
                email=ud["email"],
                username=ud["username"],
                hashed_password=get_password_hash("password123"),
                role=ud["role"],
                full_name=ud["full_name"],
                is_active=True
            )
            db.add(user)
    
    db.commit()
    return db.query(User).all()


def seed_inventory(db: Session, warehouses):
    items = [
        {"item_id": 1, "item_name": "Rice", "quantity": random.uniform(5000, 10000), "unit": "kg", "min_threshold": 2000},
        {"item_id": 2, "item_name": "Wheat", "quantity": random.uniform(3000, 8000), "unit": "kg", "min_threshold": 1500},
        {"item_id": 3, "item_name": "Pulses", "quantity": random.uniform(1000, 3000), "unit": "kg", "min_threshold": 500},
        {"item_id": 4, "item_name": "Oil", "quantity": random.uniform(500, 1500), "unit": "liters", "min_threshold": 300},
        {"item_id": 5, "item_name": "Sugar", "quantity": random.uniform(800, 2000), "unit": "kg", "min_threshold": 400},
        {"item_id": 6, "item_name": "Milk Powder", "quantity": random.uniform(200, 600), "unit": "kg", "min_threshold": 100},
    ]
    
    for warehouse in warehouses:
        for item in items:
            existing = db.query(Inventory).filter(
                Inventory.warehouse_id == warehouse.id,
                Inventory.item_id == item["item_id"]
            ).first()
            if not existing:
                inventory = Inventory(
                    warehouse_id=warehouse.id,
                    item_id=item["item_id"],
                    quantity=item["quantity"],
                    unit=item["unit"],
                    min_threshold=item["min_threshold"]
                )
                db.add(inventory)
    
    db.commit()


def seed_deliveries(db: Session, warehouses, centers):
    statuses = ["delivered", "in_transit", "pending", "scheduled", "delayed"]
    
    if not warehouses or not centers:
        return
    
    for i in range(20):
        warehouse = random.choice(warehouses)
        center = random.choice(centers)
        
        existing = db.query(Delivery).filter(
            Delivery.tracking_number == f"DEL-{random_string(8)}"
        ).first()
        
        if not existing:
            status = random.choice(statuses)
            delivery = Delivery(
                tracking_number=f"DEL-{random_string(8)}",
                warehouse_id=warehouse.id,
                destination_type="anganwadi_center",
                destination_id=center.id,
                status=status,
                scheduled_date=datetime.utcnow() + timedelta(days=random.randint(-5, 10)),
                total_weight_kg=random.uniform(100, 500),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 10))
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


def seed_trust_scores(db: Session, suppliers):
    for supplier in suppliers:
        existing = db.query(TrustScore).filter(
            TrustScore.entity_type == "supplier",
            TrustScore.entity_id == supplier.id
        ).first()
        
        if not existing:
            trust_score = TrustScore(
                entity_type="supplier",
                entity_id=supplier.id,
                score=random.uniform(3.0, 5.0),
                zone=random.choice(["green", "yellow", "red"]),
                components={"on_time_delivery": random.uniform(0.7, 0.95), "quality": random.uniform(0.7, 0.95)},
                last_updated=datetime.utcnow()
            )
            db.add(trust_score)
    
    db.commit()


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
        print("  - admin@asco.gov / password123 (Admin)")
        print("  - dpo@asco.gov / password123 (District Program Officer)")
        print("  - manager@asco.gov / password123 (Supply Chain Manager)")
        print("  - viewer@asco.gov / password123 (Viewer)")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()
