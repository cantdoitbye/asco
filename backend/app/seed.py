from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import (
    User, UserRole, District, Block, Village, Stakeholder, StakeholderType,
    AnganwadiCenter, Warehouse, Supplier, SupplyItem, Inventory, TransportFleet
)
from app.services.auth import get_password_hash
from datetime import datetime
import random


def get_or_create(db: Session, model, filter_dict, create_dict=None):
    instance = db.query(model).filter_by(**filter_dict).first()
    if instance:
        return instance, False
    if create_dict is None:
        create_dict = filter_dict
    instance = model(**create_dict)
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance, True


def seed_database():
    db: Session = SessionLocal()
    
    try:
        print("Starting database seeding...")
        
        if db.query(User).first():
            print("Database already seeded (users exist). Skipping...")
            return
        
        print("Creating districts...")
        districts = []
        district_data = [
            {"name": "Visakhapatnam", "code": "VIS"},
            {"name": "Vijayawada", "code": "VJA"},
            {"name": "Guntur", "code": "GNT"},
        ]
        for d in district_data:
            district, _ = get_or_create(db, District, {"code": d["code"]}, d)
            districts.append(district)
        
        print("Creating blocks...")
        blocks = []
        for district in districts:
            for j in range(1, 3):
                code = f"{district.code}-BLK{j}"
                block, _ = get_or_create(db, Block, {"code": code}, {
                    "name": f"{district.name} Block {j}",
                    "code": code,
                    "district_id": district.id
                })
                blocks.append(block)
        
        print("Creating villages...")
        villages = []
        for block in blocks:
            for k in range(1, 4):
                code = f"{block.code}-VIL{k}"
                village, _ = get_or_create(db, Village, {"code": code}, {
                    "name": f"Village {k} of {block.name}",
                    "code": code,
                    "block_id": block.id,
                    "population": random.randint(500, 2000)
                })
                villages.append(village)
        
        print("Creating stakeholders...")
        stakeholders = []
        stakeholder_data = [
            {"name": "State Admin Office", "type": StakeholderType.SECRETARY, "district_id": None},
            {"name": "District Collector - Visakhapatnam", "type": StakeholderType.COLLECTOR, "district_id": districts[0].id},
            {"name": "CDPO Office - Visakhapatnam", "type": StakeholderType.CDPO, "district_id": districts[0].id},
            {"name": "ABC Suppliers Pvt Ltd", "type": StakeholderType.SUPPLIER, "district_id": districts[0].id},
            {"name": "XYZ Transport", "type": StakeholderType.TRANSPORT_FLEET, "district_id": districts[0].id},
        ]
        for s in stakeholder_data:
            stakeholder, _ = get_or_create(db, Stakeholder, {"name": s["name"]}, {
                **s,
                "email": f"{s['name'].lower().replace(' ', '.').replace('-', '')}@example.com",
                "phone": f"+91{random.randint(9000000000, 9999999999)}"
            })
            stakeholders.append(stakeholder)
        
        print("Creating users...")
        users_data = [
            {
                "email": "stateadmin@ooumph.gov.in",
                "password": "admin123",
                "full_name": "State Administrator",
                "role": UserRole.STATE_ADMIN,
                "stakeholder_id": stakeholders[0].id
            },
            {
                "email": "collector@ooumph.gov.in",
                "password": "admin123",
                "full_name": "District Collector",
                "role": UserRole.DISTRICT_ADMIN,
                "stakeholder_id": stakeholders[1].id
            },
            {
                "email": "cdpo@ooumph.gov.in",
                "password": "admin123",
                "full_name": "CDPO Officer",
                "role": UserRole.BLOCK_SUPERVISOR,
                "stakeholder_id": stakeholders[2].id
            },
            {
                "email": "aww@ooumph.gov.in",
                "password": "admin123",
                "full_name": "Anganwadi Worker",
                "role": UserRole.AWW,
                "stakeholder_id": None
            },
            {
                "email": "supplier@ooumph.gov.in",
                "password": "admin123",
                "full_name": "Supplier Representative",
                "role": UserRole.SUPPLIER,
                "stakeholder_id": stakeholders[3].id
            },
        ]
        
        for u in users_data:
            user, _ = get_or_create(db, User, {"email": u["email"]}, {
                "email": u["email"],
                "hashed_password": get_password_hash(u["password"]),
                "full_name": u["full_name"],
                "role": u["role"],
                "stakeholder_id": u["stakeholder_id"],
                "is_active": True
            })
        
        print("Creating warehouses...")
        warehouses = []
        for district in districts:
            code = f"WH-{district.code}"
            warehouse, _ = get_or_create(db, Warehouse, {"code": code}, {
                "code": code,
                "name": f"{district.name} Central Warehouse",
                "district_id": district.id,
                "capacity_mt": 1000.00,
                "current_stock_mt": 500.00,
                "manager_name": f"Warehouse Manager {district.name}",
                "manager_phone": f"+91{random.randint(9000000000, 9999999999)}"
            })
            warehouses.append(warehouse)
        
        print("Creating suppliers...")
        suppliers = []
        supplier_names = ["NutriFoods India", "Grain Suppliers Co", "Dairy Products Ltd"]
        for i, name in enumerate(supplier_names):
            code = f"SUP-{i+1:03d}"
            supplier, _ = get_or_create(db, Supplier, {"code": code}, {
                "code": code,
                "name": name,
                "contact_person": f"Contact Person {i+1}",
                "email": f"contact@{name.lower().replace(' ', '')}.com",
                "phone": f"+91{random.randint(9000000000, 9999999999)}",
                "district_id": districts[i % len(districts)].id
            })
            suppliers.append(supplier)
        
        print("Creating supply items...")
        supply_items = []
        items_data = [
            {"code": "RICE-001", "name": "Rice", "category": "Grains", "unit": "kg", "unit_price": 35.00},
            {"code": "WHEAT-001", "name": "Wheat", "category": "Grains", "unit": "kg", "unit_price": 28.00},
            {"code": "DAL-001", "name": "Toor Dal", "category": "Pulses", "unit": "kg", "unit_price": 120.00},
            {"code": "OIL-001", "name": "Cooking Oil", "category": "Oil", "unit": "liter", "unit_price": 150.00},
            {"code": "MILK-001", "name": "Milk Powder", "category": "Dairy", "unit": "kg", "unit_price": 400.00},
        ]
        for item in items_data:
            supply_item, _ = get_or_create(db, SupplyItem, {"code": item["code"]}, item)
            supply_items.append(supply_item)
        
        print("Creating Anganwadi centers...")
        anganwadi_centers = []
        for village in villages[:6]:
            code = f"AWC-{village.code}"
            center, _ = get_or_create(db, AnganwadiCenter, {"code": code}, {
                "code": code,
                "name": f"Anganwadi Center {village.name}",
                "village_id": village.id,
                "aww_name": f"Worker for {village.name}",
                "aww_phone": f"+91{random.randint(9000000000, 9999999999)}",
                "total_beneficiaries": random.randint(30, 100),
                "children_0_3": random.randint(10, 30),
                "children_3_6": random.randint(15, 40),
                "pregnant_women": random.randint(5, 15),
                "lactating_mothers": random.randint(5, 15)
            })
            anganwadi_centers.append(center)
        
        print("Creating transport fleets...")
        fleets = []
        for i, warehouse in enumerate(warehouses):
            for j in range(1, 3):
                vehicle_number = f"AP{random.randint(10, 99)}{random.choice(['AB', 'CD', 'EF'])}{random.randint(1000, 9999)}"
                fleet, _ = get_or_create(db, TransportFleet, {"vehicle_number": vehicle_number}, {
                    "vehicle_number": vehicle_number,
                    "vehicle_type": "Truck" if j == 1 else "Mini Van",
                    "driver_name": f"Driver {i}-{j}",
                    "driver_phone": f"+91{random.randint(9000000000, 9999999999)}",
                    "capacity_kg": 5000.00 if j == 1 else 2000.00,
                    "warehouse_id": warehouse.id
                })
                fleets.append(fleet)
        
        print("Creating inventory...")
        for warehouse in warehouses:
            for item in supply_items:
                existing = db.query(Inventory).filter(
                    Inventory.warehouse_id == warehouse.id,
                    Inventory.item_id == item.id
                ).first()
                if not existing:
                    inventory = Inventory(
                        item_id=item.id,
                        warehouse_id=warehouse.id,
                        quantity=random.uniform(100, 500),
                        min_threshold=50.00,
                        max_threshold=1000.00
                    )
                    db.add(inventory)
        db.commit()
        
        print("\n" + "="*50)
        print("DATABASE SEEDED SUCCESSFULLY!")
        print("="*50)
        print("\nLogin Credentials:")
        print("-" * 40)
        print("1. State Admin:")
        print("   Email: stateadmin@ooumph.gov.in")
        print("   Password: admin123")
        print("-" * 40)
        print("2. District Collector:")
        print("   Email: collector@ooumph.gov.in")
        print("   Password: admin123")
        print("-" * 40)
        print("3. CDPO Officer:")
        print("   Email: cdpo@ooumph.gov.in")
        print("   Password: admin123")
        print("-" * 40)
        print("4. Anganwadi Worker:")
        print("   Email: aww@ooumph.gov.in")
        print("   Password: admin123")
        print("-" * 40)
        print("5. Supplier:")
        print("   Email: supplier@ooumph.gov.in")
        print("   Password: admin123")
        print("="*50)
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
