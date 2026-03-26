from datetime import datetime, timedelta
from typing import Dict, List, Optional
from decimal import Decimal
import random


class PoshanTrackerStub:
    def __init__(self):
        self.base_url = "https://poshantracker.gov.in/api/v1"
    
    async def get_beneficiary_data(self, anganwadi_id: int) -> Dict:
        return {
            "anganwadi_id": anganwadi_id,
            "total_beneficiaries": random.randint(50, 200),
            "children_0_3": random.randint(15, 50),
            "children_3_6": random.randint(20, 60),
            "pregnant_women": random.randint(5, 20),
            "lactating_mothers": random.randint(8, 25),
            "last_updated": datetime.utcnow().isoformat(),
            "data_source": "POSHAN_TRACKER_STUB"
        }
    
    async def get_nutrition_status(self, anganwadi_id: int) -> Dict:
        statuses = ["normal", "moderate", "severe"]
        children_count = random.randint(30, 80)
        return {
            "anganwadi_id": anganwadi_id,
            "nutrition_screening": {
                "total_children": children_count,
                "normal": random.randint(int(children_count * 0.6), int(children_count * 0.8)),
                "moderate": random.randint(int(children_count * 0.1), int(children_count * 0.2)),
                "severe": random.randint(0, int(children_count * 0.1)),
            },
            "last_screening_date": (datetime.utcnow() - timedelta(days=random.randint(1, 30))).isoformat(),
            "data_source": "POSHAN_TRACKER_STUB"
        }
    
    async def get_growth_metrics(self, child_id: int) -> Dict:
        return {
            "child_id": child_id,
            "height_cm": round(random.uniform(60, 110), 1),
            "weight_kg": round(random.uniform(8, 20), 1),
            "bmi": round(random.uniform(13, 18), 1),
            "growth_status": random.choice(["normal", "underweight", "stunted", "wasted"]),
            "measurement_date": datetime.utcnow().isoformat(),
            "data_source": "POSHAN_TRACKER_STUB"
        }
    
    async def get_supplementation_records(self, anganwadi_id: int) -> Dict:
        return {
            "anganwadi_id": anganwadi_id,
            "take_home_ration": {
                "distributed": random.randint(100, 500),
                "pending": random.randint(10, 50),
                "last_distribution": (datetime.utcnow() - timedelta(days=random.randint(1, 7))).isoformat()
            },
            "hot_cooked_meals": {
                "served_today": random.randint(30, 100),
                "avg_daily": random.randint(40, 80)
            },
            "data_source": "POSHAN_TRACKER_STUB"
        }


poshan_tracker_stub = PoshanTrackerStub()
