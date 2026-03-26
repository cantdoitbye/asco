from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
from ...database import get_db
from ...services.auth import get_current_user
from ...models import User
from ...services.ai.agents.community_coordination import community_coordination_agent

router = APIRouter()


class StakeholderCreate(BaseModel):
    name: str
    type: str
    department: Optional[str] = None
    role: Optional[str] = None
    contact: Optional[str] = None
    district_id: Optional[int] = None
    block_id: Optional[int] = None


class ConnectionCreate(BaseModel):
    stakeholder_1_id: int
    stakeholder_2_id: int
    connection_type: str
    strength: Optional[int] = None


class MeetingCreate(BaseModel):
    title: str
    description: Optional[str] = None
    scheduled_at: datetime
    duration_minutes: Optional[int] = 60
    location: Optional[str] = None
    meeting_type: str = "in_person"
    organizer_id: Optional[int] = None
    attendees: List[int] = []
    agenda: Optional[List[str]] = None


class NotificationMarkRead(BaseModel):
    notification_id: int


def get_mock_network_data():
    now = datetime.utcnow()
    return {
        "stakeholders": [
            {"id": "1", "name": "District Collector", "type": "government", "department": "Administration", "role": "District Collector", "contact": "collector@district.gov", "district_id": 1, "registered_at": (now - timedelta(days=90)).isoformat()},
            {"id": "2", "name": "CDPO Hyderabad", "type": "government", "department": "ICDS", "role": "Child Development Project Officer", "contact": "cdpo.hyderabad@icds.gov", "district_id": 1, "registered_at": (now - timedelta(days=85)).isoformat()},
            {"id": "3", "name": "Medical Officer", "type": "healthcare", "department": "Health", "role": "Medical Officer", "contact": "mo@health.gov", "district_id": 1, "registered_at": (now - timedelta(days=80)).isoformat()},
            {"id": "4", "name": "Supply Chain Manager", "type": "logistics", "department": "Supply Chain", "role": "Manager", "contact": "scm@supply.gov", "district_id": 1, "registered_at": (now - timedelta(days=75)).isoformat()},
            {"id": "5", "name": "NGO Partner - Child Health", "type": "ngo", "department": "Healthcare", "role": "Program Manager", "contact": "ngo.health@partner.org", "district_id": 1, "registered_at": (now - timedelta(days=70)).isoformat()},
            {"id": "6", "name": "Block Development Officer", "type": "government", "department": "Rural Development", "role": "BDO", "contact": "bdo@block.gov", "district_id": 1, "block_id": 1, "registered_at": (now - timedelta(days=65)).isoformat()},
            {"id": "7", "name": "Warehouse Supervisor", "type": "logistics", "department": "Warehouse", "role": "Supervisor", "contact": "warehouse@supply.gov", "district_id": 1, "registered_at": (now - timedelta(days=60)).isoformat()},
            {"id": "8", "name": "Women & Child Welfare Officer", "type": "government", "department": "WCD", "role": "Welfare Officer", "contact": "wcw@wcd.gov", "district_id": 1, "registered_at": (now - timedelta(days=55)).isoformat()},
        ],
        "connections": [
            {"id": "conn-1", "source": "1", "target": "2", "type": "supervision", "strength": 0.9, "created_at": (now - timedelta(days=80)).isoformat()},
            {"id": "conn-2", "source": "2", "target": "3", "type": "coordination", "strength": 0.8, "created_at": (now - timedelta(days=75)).isoformat()},
            {"id": "conn-3", "source": "2", "target": "4", "type": "collaboration", "strength": 0.85, "created_at": (now - timedelta(days=70)).isoformat()},
            {"id": "conn-4", "source": "4", "target": "7", "type": "supervision", "strength": 0.9, "created_at": (now - timedelta(days=65)).isoformat()},
            {"id": "conn-5", "source": "5", "target": "3", "type": "partnership", "strength": 0.75, "created_at": (now - timedelta(days=60)).isoformat()},
            {"id": "conn-6", "source": "6", "target": "2", "type": "coordination", "strength": 0.8, "created_at": (now - timedelta(days=55)).isoformat()},
            {"id": "conn-7", "source": "8", "target": "2", "type": "collaboration", "strength": 0.85, "created_at": (now - timedelta(days=50)).isoformat()},
            {"id": "conn-8", "source": "1", "target": "6", "type": "supervision", "strength": 0.9, "created_at": (now - timedelta(days=45)).isoformat()},
        ],
        "stats": {
            "total_stakeholders": 8,
            "total_connections": 8,
            "average_connections": 2.0
        }
    }


def get_mock_meetings():
    now = datetime.utcnow()
    return [
        {"id": "meet-1", "title": "Monthly Supply Review", "description": "Review supply chain performance for the month", "scheduled_at": (now + timedelta(days=2)).isoformat(), "duration_minutes": 90, "location": "District Office", "meeting_type": "in_person", "organizer_id": 1, "attendees": [2, 4, 7], "status": "scheduled", "created_at": (now - timedelta(days=5)).isoformat()},
        {"id": "meet-2", "title": "Nutrition Program Planning", "description": "Quarterly nutrition program planning meeting", "scheduled_at": (now + timedelta(days=5)).isoformat(), "duration_minutes": 120, "location": "Conference Room A", "meeting_type": "in_person", "organizer_id": 2, "attendees": [3, 5, 8], "status": "scheduled", "created_at": (now - timedelta(days=3)).isoformat()},
        {"id": "meet-3", "title": "Grievance Review Committee", "description": "Weekly grievance review and resolution", "scheduled_at": (now + timedelta(days=1)).isoformat(), "duration_minutes": 60, "location": "Virtual", "meeting_type": "virtual", "organizer_id": 1, "attendees": [2, 6], "status": "scheduled", "created_at": (now - timedelta(days=1)).isoformat()},
        {"id": "meet-4", "title": "Block Coordination Meeting", "description": "Coordination meeting with block officers", "scheduled_at": (now + timedelta(days=7)).isoformat(), "duration_minutes": 90, "location": "Block Office", "meeting_type": "in_person", "organizer_id": 6, "attendees": [1, 2], "status": "scheduled", "created_at": now.isoformat()},
    ]


@router.get("/stakeholders")
async def get_stakeholders(
    district_id: Optional[int] = Query(None),
    stakeholder_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = community_coordination_agent.get_stakeholder_network(
        stakeholder_id=stakeholder_id,
        district_id=district_id
    )
    
    if not result.get("stakeholders"):
        return get_mock_network_data()
    
    return result


@router.post("/stakeholders")
async def create_stakeholder(
    stakeholder: StakeholderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stakeholder_data = {
        "name": stakeholder.name,
        "type": stakeholder.type,
        "department": stakeholder.department,
        "role": stakeholder.role,
        "contact": stakeholder.contact,
        "district_id": stakeholder.district_id,
        "block_id": stakeholder.block_id,
        "created_by": current_user.id,
        "created_at": datetime.utcnow().isoformat()
    }
    
    result = community_coordination_agent.register_stakeholder(stakeholder_data)
    
    return {
        "message": "Stakeholder registered successfully",
        "stakeholder": result
    }


@router.post("/connections")
async def create_connection(
    connection: ConnectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    connection_data = {
        "stakeholder_1_id": connection.stakeholder_1_id,
        "stakeholder_2_id": connection.stakeholder_2_id,
        "connection_type": connection.connection_type,
        "strength": connection.strength,
        "created_by": current_user.id,
        "created_at": datetime.utcnow().isoformat()
    }
    
    result = community_coordination_agent.create_connection(connection_data)
    
    return {
        "message": "Connection created successfully",
        "connection": result
    }


@router.get("/meetings")
async def get_meetings(
    district_id: Optional[int] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = community_coordination_agent.get_upcoming_meetings(
        stakeholder_id=str(current_user.id),
        limit=limit
    )
    
    if not result:
        return {"meetings": get_mock_meetings(), "total": len(get_mock_meetings())}
    
    return {
        "meetings": result,
        "total": len(result)
    }


@router.post("/meetings")
async def create_meeting(
    meeting: MeetingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meeting_data = {
        "title": meeting.title,
        "description": meeting.description,
        "scheduled_at": meeting.scheduled_at.isoformat(),
        "duration_minutes": meeting.duration_minutes,
        "location": meeting.location,
        "meeting_type": meeting.meeting_type,
        "organizer_id": meeting.organizer_id or current_user.id,
        "attendees": meeting.attendees,
        "agenda": meeting.agenda,
        "created_by": current_user.id,
        "created_at": datetime.utcnow().isoformat()
    }
    
    result = await community_coordination_agent.schedule_meeting(meeting_data)
    
    return {
        "message": "Meeting scheduled successfully",
        "meeting": result
    }


@router.get("/notifications")
async def get_notifications(
    recipient_id: Optional[int] = Query(None),
    unread_only: bool = Query(False),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = community_coordination_agent.get_notifications(
        recipient_id=str(recipient_id or current_user.id),
        unread_only=unread_only,
        limit=limit
    )
    
    return {
        "notifications": result,
        "total": len(result)
    }


@router.post("/notifications/read")
async def mark_notification_read(
    notification: NotificationMarkRead,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = community_coordination_agent.mark_notification_read(
        str(notification.notification_id)
    )
    
    return {
        "message": "Notification marked as read",
        "notification_id": notification.notification_id,
        "result": result
    }
