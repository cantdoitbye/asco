from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import math

from sqlalchemy.orm import Session
from sqlalchemy import func

from ..utils.logger import get_logger
from ..models import Supplier, TransportFleet, AnganwadiCenter, User, Delivery, Grievance

logger = get_logger(__name__)


class TrustZone(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"
    RED = "red"


class TrustScoreService:
    def __init__(self):
        self.zone_thresholds = {
            TrustZone.GREEN: (4.0, 5.0),
            TrustZone.YELLOW: (3.0, 3.9),
            TrustZone.ORANGE: (2.0, 2.9),
            TrustZone.RED: (0.0, 1.9)
        }

    def get_zone(self, score: float) -> TrustZone:
        if score >= 4.0:
            return TrustZone.GREEN
        elif score >= 3.0:
            return TrustZone.YELLOW
        elif score >= 2.0:
            return TrustZone.ORANGE
        else:
            return TrustZone.RED

    async def calculate_supplier_score(
        self,
        supplier_id: int,
        db: Session
    ) -> Dict[str, Any]:
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            return {"error": "Supplier not found"}

        on_time_rate = 0.85
        grievances = db.query(Grievance).filter(
            Grievance.entity_type == "supplier",
            Grievance.entity_id == supplier_id
        ).count()

        grievance_penalty = min(grievances * 0.2, 1.0)

        on_time_score = on_time_rate * 5.0
        quality_score = 4.0
        quantity_score = 4.0
        grievance_score = max(0, 5.0 - grievance_penalty * 5)

        weights = {
            "on_time_delivery": 0.4,
            "quality_compliance": 0.25,
            "quantity_accuracy": 0.15,
            "grievance_frequency": 0.2
        }

        final_score = (
            on_time_score * weights["on_time_delivery"] +
            quality_score * weights["quality_compliance"] +
            quantity_score * weights["quantity_accuracy"] +
            grievance_score * weights["grievance_frequency"]
        )

        final_score = max(0.0, min(5.0, final_score))

        return {
            "supplier_id": supplier_id,
            "supplier_name": supplier.name,
            "score": round(final_score, 2),
            "zone": self.get_zone(final_score).value,
            "components": {
                "on_time_delivery_rate": round(on_time_rate * 100, 1),
                "on_time_score": round(on_time_score, 2),
                "quality_score": round(quality_score, 2),
                "quantity_score": round(quantity_score, 2),
                "grievance_count": grievances,
                "grievance_score": round(grievance_score, 2)
            },
            "weights": weights,
            "calculated_at": datetime.utcnow().isoformat()
        }

    async def calculate_transport_fleet_score(
        self,
        fleet_id: int,
        db: Session
    ) -> Dict[str, Any]:
        fleet = db.query(TransportFleet).filter(TransportFleet.id == fleet_id).first()
        if not fleet:
            return {"error": "Transport fleet not found"}

        deliveries = db.query(Delivery).filter(
            Delivery.transport_fleet_id == fleet_id
        ).all()

        if not deliveries:
            return {
                "fleet_id": fleet_id,
                "score": 3.0,
                "zone": "yellow",
                "components": {},
                "message": "No delivery data available"
            }

        total_deliveries = len(deliveries)
        completed = sum(1 for d in deliveries if d.status == "delivered")
        completion_rate = completed / total_deliveries if total_deliveries > 0 else 0

        route_adherence = 0.85
        vehicle_condition = 4.0
        fuel_efficiency = 3.5

        completion_score = completion_rate * 5.0
        route_score = route_adherence * 5.0

        weights = {
            "route_adherence": 0.25,
            "delivery_completion": 0.35,
            "vehicle_condition": 0.2,
            "fuel_efficiency": 0.2
        }

        final_score = (
            route_score * weights["route_adherence"] +
            completion_score * weights["delivery_completion"] +
            vehicle_condition * weights["vehicle_condition"] +
            fuel_efficiency * weights["fuel_efficiency"]
        )

        final_score = max(0.0, min(5.0, final_score))

        return {
            "fleet_id": fleet_id,
            "vehicle_number": fleet.vehicle_number,
            "score": round(final_score, 2),
            "zone": self.get_zone(final_score).value,
            "components": {
                "route_adherence_rate": round(route_adherence * 100, 1),
                "route_score": round(route_score, 2),
                "completion_rate": round(completion_rate * 100, 1),
                "completion_score": round(completion_score, 2),
                "vehicle_condition_score": vehicle_condition,
                "fuel_efficiency_score": fuel_efficiency
            },
            "weights": weights,
            "total_deliveries": total_deliveries,
            "calculated_at": datetime.utcnow().isoformat()
        }

    async def calculate_anganwadi_worker_score(
        self,
        center_id: int,
        db: Session
    ) -> Dict[str, Any]:
        center = db.query(AnganwadiCenter).filter(AnganwadiCenter.id == center_id).first()
        if not center:
            return {"error": "Anganwadi center not found"}

        data_submission_score = 4.0
        offline_sync_score = 4.0
        attendance_tracking_score = 3.5
        complaint_resolution_score = 4.0

        weights = {
            "data_submission": 0.3,
            "offline_sync": 0.25,
            "attendance_tracking": 0.25,
            "complaint_resolution": 0.2
        }

        final_score = (
            data_submission_score * weights["data_submission"] +
            offline_sync_score * weights["offline_sync"] +
            attendance_tracking_score * weights["attendance_tracking"] +
            complaint_resolution_score * weights["complaint_resolution"]
        )

        final_score = max(0.0, min(5.0, final_score))

        return {
            "center_id": center_id,
            "center_name": center.name,
            "score": round(final_score, 2),
            "zone": self.get_zone(final_score).value,
            "components": {
                "data_submission_score": data_submission_score,
                "offline_sync_score": offline_sync_score,
                "attendance_tracking_score": attendance_tracking_score,
                "complaint_resolution_score": complaint_resolution_score
            },
            "weights": weights,
            "calculated_at": datetime.utcnow().isoformat()
        }

    async def calculate_supervisor_score(
        self,
        user_id: int,
        db: Session
    ) -> Dict[str, Any]:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}

        response_time_score = 4.0
        monitoring_visit_score = 3.5
        grievance_resolution_score = 4.0
        report_timeliness_score = 4.5

        weights = {
            "response_time": 0.3,
            "monitoring_visits": 0.25,
            "grievance_resolution": 0.25,
            "report_timeliness": 0.2
        }

        final_score = (
            response_time_score * weights["response_time"] +
            monitoring_visit_score * weights["monitoring_visits"] +
            grievance_resolution_score * weights["grievance_resolution"] +
            report_timeliness_score * weights["report_timeliness"]
        )

        final_score = max(0.0, min(5.0, final_score))

        return {
            "user_id": user_id,
            "user_name": user.full_name,
            "score": round(final_score, 2),
            "zone": self.get_zone(final_score).value,
            "components": {
                "response_time_score": response_time_score,
                "monitoring_visit_score": monitoring_visit_score,
                "grievance_resolution_score": grievance_resolution_score,
                "report_timeliness_score": report_timeliness_score
            },
            "weights": weights,
            "calculated_at": datetime.utcnow().isoformat()
        }

    async def get_all_scores(
        self,
        entity_type: Optional[str] = None,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        scores = []

        if entity_type is None or entity_type == "supplier":
            suppliers = db.query(Supplier).all()
            for supplier in suppliers[:10]:
                score = await self.calculate_supplier_score(supplier.id, db)
                if "error" not in score:
                    score["entity_type"] = "supplier"
                    scores.append(score)

        if entity_type is None or entity_type == "transport_fleet":
            fleets = db.query(TransportFleet).all()
            for fleet in fleets[:10]:
                score = await self.calculate_transport_fleet_score(fleet.id, db)
                if "error" not in score:
                    score["entity_type"] = "transport_fleet"
                    scores.append(score)

        if entity_type is None or entity_type == "anganwadi_center":
            centers = db.query(AnganwadiCenter).all()
            for center in centers[:10]:
                score = await self.calculate_anganwadi_worker_score(center.id, db)
                if "error" not in score:
                    score["entity_type"] = "anganwadi_center"
                    scores.append(score)

        return scores


trust_score_service = TrustScoreService()
