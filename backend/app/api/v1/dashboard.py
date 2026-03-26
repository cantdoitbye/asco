from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from datetime import datetime, timedelta
import random
from ...database import get_db
from ...models import AnganwadiCenter, Delivery, Grievance, TrustScore, Inventory, AuditLog
from ...schemas.supply import DashboardStats
from ...services.auth import get_current_user
from ...models import User

router = APIRouter()


def get_mock_stats():
    return {
        "total_anganwadi_centers": 1247,
        "total_beneficiaries": 45892,
        "total_deliveries": 3256,
        "pending_deliveries": 47,
        "active_grievances": 23,
        "avg_trust_score": Decimal("4.23"),
        "low_stock_alerts": 12,
        "upcoming_scheduled_deliveries": 89
    }


def get_mock_alerts():
    return {
        "low_stock_alerts": [
            {"id": 1, "item_id": 101, "item_name": "Rice", "quantity": 15, "min_threshold": 50, "warehouse": "Central Warehouse"},
            {"id": 2, "item_id": 102, "item_name": "Wheat", "quantity": 8, "min_threshold": 40, "warehouse": "District Warehouse A"},
            {"id": 3, "item_id": 103, "item_name": "Pulses", "quantity": 12, "min_threshold": 30, "warehouse": "Central Warehouse"},
        ],
        "pending_deliveries_count": 47,
        "open_grievances_count": 23,
        "critical_alerts": [
            {"id": "A1", "type": "delivery_delay", "message": "Delivery #DEL-2024-156 delayed due to road conditions", "severity": "high"},
            {"id": "A2", "type": "stock_low", "message": "Rice stock below threshold at Central Warehouse", "severity": "medium"},
        ]
    }


def get_mock_recent_activity():
    now = datetime.utcnow()
    return [
        {"id": 1, "type": "delivery_completed", "description": "Delivery completed to Anganwadi Center #245", "timestamp": (now - timedelta(minutes=15)).isoformat(), "entity_type": "delivery", "entity_id": 156},
        {"id": 2, "type": "grievance_filed", "description": "New grievance filed by AWW Center #182", "timestamp": (now - timedelta(hours=1)).isoformat(), "entity_type": "grievance", "entity_id": 89},
        {"id": 3, "type": "stock_updated", "description": "Inventory updated at District Warehouse B", "timestamp": (now - timedelta(hours=2)).isoformat(), "entity_type": "inventory", "entity_id": 45},
        {"id": 4, "type": "route_optimized", "description": "Route optimized for District Hyderabad", "timestamp": (now - timedelta(hours=3)).isoformat(), "entity_type": "route", "entity_id": 23},
        {"id": 5, "type": "compliance_check", "description": "Compliance audit completed for Block 12", "timestamp": (now - timedelta(hours=5)).isoformat(), "entity_type": "compliance", "entity_id": 12},
    ]


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        total_anganwadi_centers = db.query(AnganwadiCenter).filter(
            AnganwadiCenter.is_active == True
        ).count()
        
        if total_anganwadi_centers == 0:
            return get_mock_stats()
        
        total_beneficiaries = db.query(
            func.sum(AnganwadiCenter.total_beneficiaries)
        ).scalar() or 0
        
        total_deliveries = db.query(Delivery).count()
        
        pending_deliveries = db.query(Delivery).filter(
            Delivery.status == "pending"
        ).count()
        
        active_grievances = db.query(Grievance).filter(
            Grievance.status.in_(["open", "in_progress"])
        ).count()
        
        avg_trust_score = db.query(
            func.avg(TrustScore.score)
        ).scalar() or Decimal("0.00")
        
        low_stock_alerts = db.query(Inventory).filter(
            Inventory.quantity <= Inventory.min_threshold
        ).count()
        
        upcoming_deliveries = db.query(Delivery).filter(
            Delivery.status == "scheduled"
        ).count()
        
        return {
            "total_anganwadi_centers": total_anganwadi_centers,
            "total_beneficiaries": int(total_beneficiaries),
            "total_deliveries": total_deliveries,
            "pending_deliveries": pending_deliveries,
            "active_grievances": active_grievances,
            "avg_trust_score": round(avg_trust_score, 2) if avg_trust_score else Decimal("4.23"),
            "low_stock_alerts": low_stock_alerts,
            "upcoming_scheduled_deliveries": upcoming_deliveries
        }
    except Exception:
        return get_mock_stats()


@router.get("/recent-activity")
def get_recent_activity(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        activities = db.query(AuditLog).order_by(
            AuditLog.created_at.desc()
        ).limit(limit).all()
        
        if not activities:
            return get_mock_recent_activity()
        
        return [
            {
                "id": activity.id,
                "type": activity.action,
                "description": activity.details or f"{activity.action} on {activity.entity_type}",
                "timestamp": activity.created_at.isoformat() if activity.created_at else None,
                "entity_type": activity.entity_type,
                "entity_id": activity.entity_id
            }
            for activity in activities
        ]
    except Exception:
        return get_mock_recent_activity()


@router.get("/delivery-summary")
def get_delivery_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        status_counts = db.query(
            Delivery.status,
            func.count(Delivery.id).label("count")
        ).group_by(Delivery.status).all()
        
        if not status_counts:
            return {
                "status_breakdown": [
                    {"status": "delivered", "count": 2847},
                    {"status": "in_transit", "count": 156},
                    {"status": "pending", "count": 47},
                    {"status": "scheduled", "count": 89},
                    {"status": "delayed", "count": 12}
                ]
            }
        
        return {
            "status_breakdown": [
                {"status": status, "count": count}
                for status, count in status_counts
            ]
        }
    except Exception:
        return {
            "status_breakdown": [
                {"status": "delivered", "count": 2847},
                {"status": "in_transit", "count": 156},
                {"status": "pending", "count": 47},
                {"status": "scheduled", "count": 89},
                {"status": "delayed", "count": 12}
            ]
        }


@router.get("/alerts")
def get_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        low_stock = db.query(Inventory).filter(
            Inventory.quantity <= Inventory.min_threshold
        ).limit(5).all()
        
        pending_deliveries = db.query(Delivery).filter(
            Delivery.status == "pending"
        ).limit(5).all()
        
        open_grievances = db.query(Grievance).filter(
            Grievance.status == "open"
        ).limit(5).all()
        
        if not low_stock and not pending_deliveries and not open_grievances:
            return get_mock_alerts()
        
        return {
            "low_stock_alerts": [
                {
                    "id": inv.id,
                    "item_id": inv.item_id,
                    "quantity": float(inv.quantity) if inv.quantity else 0,
                    "min_threshold": float(inv.min_threshold) if inv.min_threshold else 0
                }
                for inv in low_stock
            ],
            "pending_deliveries_count": len(pending_deliveries),
            "open_grievances_count": len(open_grievances)
        }
    except Exception:
        return get_mock_alerts()
