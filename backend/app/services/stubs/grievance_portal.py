from typing import Dict, Any, List, Optional
from datetime import datetime
import random

from ....utils.logger import get_logger

logger = get_logger(__name__)


class GrievancePortalStub:
    def __init__(self):
        self.base_url = "https://pgportal.gov.in"
        self.mock_complaints = []
        self._generate_mock_data()

    def _generate_mock_data(self):
        self.mock_complaints = [
            {
                "id": "CP-2024-001",
                "complainant_name": "Ramesh Kumar",
                "complainant_phone": "9876543210",
                "complaint": "THR ration not received for last 2 months at Anganwadi Center in Village Rampur",
                "category": "supply_shortage",
                "status": "pending",
                "priority": "high",
                "district": "Krishna",
                "block": "Vijayawada Rural",
                "created_at": "2024-01-15T10:30:00Z",
                "source": "pg_portal"
            },
            {
                "id": "CP-2024-002",
                "complainant_name": "Lakshmi Devi",
                "complainant_phone": "9123456780",
                "complaint": "Take Home Ration quality is poor and children are refusing to eat",
                "category": "quality_issue",
                "status": "under_investigation",
                "priority": "high",
                "district": "Guntur",
                "block": "Mangalagiri",
                "created_at": "2024-01-14T14:45:00Z",
                "source": "pg_portal"
            },
            {
                "id": "CP-2024-003",
                "complainant_name": "Venkat Rao",
                "complainant_phone": "9988776655",
                "complaint": "Anganwadi worker is irregular and center remains closed during duty hours",
                "category": "staff_behavior",
                "status": "resolved",
                "priority": "medium",
                "district": "East Godavari",
                "block": "Kakinada Rural",
                "created_at": "2024-01-10T09:15:00Z",
                "resolved_at": "2024-01-12T16:30:00Z",
                "resolution": "Worker counseled and attendance monitoring system implemented",
                "source": "pg_portal"
            }
        ]

    async def get_complaints(
        self,
        status: Optional[str] = None,
        district: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        complaints = self.mock_complaints.copy()
        
        if status:
            complaints = [c for c in complaints if c.get("status") == status]
        if district:
            complaints = [c for c in complaints if c.get("district") == district]
        
        return complaints[:limit]

    async def get_complaint_by_id(self, complaint_id: str) -> Optional[Dict[str, Any]]:
        for complaint in self.mock_complaints:
            if complaint.get("id") == complaint_id:
                return complaint
        return None

    async def create_complaint(
        self,
        complaint_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        new_id = f"CP-2024-{random.randint(100, 999)}"
        new_complaint = {
            "id": new_id,
            "complainant_name": complaint_data.get("complainant_name", "Anonymous"),
            "complainant_phone": complaint_data.get("complainant_phone"),
            "complaint": complaint_data.get("complaint"),
            "category": complaint_data.get("category", "general"),
            "status": "pending",
            "priority": complaint_data.get("priority", "medium"),
            "district": complaint_data.get("district"),
            "block": complaint_data.get("block"),
            "created_at": datetime.utcnow().isoformat() + "Z",
            "source": "pg_portal"
        }
        
        self.mock_complaints.append(new_complaint)
        
        return new_complaint

    async def update_complaint_status(
        self,
        complaint_id: str,
        status: str,
        resolution: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        for complaint in self.mock_complaints:
            if complaint.get("id") == complaint_id:
                complaint["status"] = status
                if resolution:
                    complaint["resolution"] = resolution
                    complaint["resolved_at"] = datetime.utcnow().isoformat() + "Z"
                return complaint
        return None

    async def get_statistics(self) -> Dict[str, Any]:
        total = len(self.mock_complaints)
        pending = len([c for c in self.mock_complaints if c.get("status") == "pending"])
        resolved = len([c for c in self.mock_complaints if c.get("status") == "resolved"])
        
        return {
            "total_complaints": total,
            "pending": pending,
            "under_investigation": len([c for c in self.mock_complaints if c.get("status") == "under_investigation"]),
            "resolved": resolved,
            "resolution_rate": round((resolved / total) * 100, 1) if total > 0 else 0,
            "by_category": {
                "supply_shortage": len([c for c in self.mock_complaints if c.get("category") == "supply_shortage"]),
                "quality_issue": len([c for c in self.mock_complaints if c.get("category") == "quality_issue"]),
                "staff_behavior": len([c for c in self.mock_complaints if c.get("category") == "staff_behavior"])
            },
            "by_district": {
                "Krishna": len([c for c in self.mock_complaints if c.get("district") == "Krishna"]),
                "Guntur": len([c for c in self.mock_complaints if c.get("district") == "Guntur"]),
                "East Godavari": len([c for c in self.mock_complaints if c.get("district") == "East Godavari"])
            }
        }


grievance_portal_stub = GrievancePortalStub()
