from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random


class ICDCASStub:
    def __init__(self):
        self.base_url = "https://icds-cas.gov.in/api/v1"
    
    async def get_scheme_data(self, district_id: int) -> Dict:
        return {
            "district_id": district_id,
            "schemes": [
                {
                    "name": "Supplementary Nutrition Programme",
                    "code": "SNP",
                    "beneficiaries": random.randint(5000, 20000),
                    "budget_allocated": random.randint(1000000, 5000000),
                    "budget_utilized": random.randint(800000, 4500000)
                },
                {
                    "name": "Immunization Programme",
                    "code": "IP",
                    "beneficiaries": random.randint(2000, 10000),
                    "budget_allocated": random.randint(500000, 2000000),
                    "budget_utilized": random.randint(400000, 1800000)
                },
                {
                    "name": "Health Check-up",
                    "code": "HCU",
                    "beneficiaries": random.randint(3000, 15000),
                    "budget_allocated": random.randint(300000, 1000000),
                    "budget_utilized": random.randint(250000, 900000)
                }
            ],
            "last_updated": datetime.utcnow().isoformat(),
            "data_source": "ICDS_CAS_STUB"
        }
    
    async def get_beneficiary_tracking(self, beneficiary_id: int) -> Dict:
        return {
            "beneficiary_id": beneficiary_id,
            "name": f"Beneficiary_{beneficiary_id}",
            "type": random.choice(["child", "pregnant_woman", "lactating_mother"]),
            "anganwadi_center": f"AWC_{random.randint(1, 100)}",
            "registration_date": (datetime.utcnow() - timedelta(days=random.randint(100, 1000))).isoformat(),
            "services_availed": random.randint(10, 100),
            "last_visit": (datetime.utcnow() - timedelta(days=random.randint(1, 30))).isoformat(),
            "data_source": "ICDS_CAS_STUB"
        }
    
    async def get_service_delivery_status(self, anganwadi_id: int) -> Dict:
        return {
            "anganwadi_id": anganwadi_id,
            "services": {
                "supplementary_nutrition": {
                    "target": random.randint(100, 200),
                    "achieved": random.randint(80, 190),
                    "percentage": round(random.uniform(70, 100), 1)
                },
                "immunization": {
                    "target": random.randint(50, 100),
                    "achieved": random.randint(40, 95),
                    "percentage": round(random.uniform(70, 100), 1)
                },
                "health_checkup": {
                    "target": random.randint(60, 120),
                    "achieved": random.randint(50, 110),
                    "percentage": round(random.uniform(70, 100), 1)
                }
            },
            "last_updated": datetime.utcnow().isoformat(),
            "data_source": "ICDS_CAS_STUB"
        }
    
    async def get_monthly_progress_report(self, district_id: int, month: int, year: int) -> Dict:
        return {
            "district_id": district_id,
            "period": {"month": month, "year": year},
            "summary": {
                "total_anganwadis": random.randint(200, 500),
                "active_anganwadis": random.randint(180, 480),
                "total_beneficiaries": random.randint(10000, 50000),
                "services_delivered": random.randint(50000, 200000)
            },
            "performance_score": round(random.uniform(70, 95), 1),
            "generated_at": datetime.utcnow().isoformat(),
            "data_source": "ICDS_CAS_STUB"
        }


icds_cas_stub = ICDCASStub()
