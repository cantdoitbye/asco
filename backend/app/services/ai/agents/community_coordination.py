from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import json
import uuid

from ..base_agent import BaseAIAgent, AgentResponse
from ..openai_client import OpenAIClient
from ....utils.logger import get_logger

logger = get_logger(__name__)


class MeetingStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"


class NotificationType(str, Enum):
    MEETING_INVITE = "meeting_invite"
    MEETING_REMINDER = "meeting_reminder"
    TASK_ASSIGNMENT = "task_assignment"
    SYSTEM_ALERT = "system_alert"
    COMPLIANCE_UPDATE = "compliance_update"
    DELIVERY_UPDATE = "delivery_update"


COMMUNITY_SYSTEM_PROMPT = """You are the Community Coordination Agent for the Ooumph SHAKTI supply chain management system.
Your role is to facilitate cross-department coordination, manage stakeholder relationships, and handle meeting scheduling.

You have expertise in:
- Stakeholder relationship management
- Meeting coordination and scheduling
- Cross-department communication
- Notification management
- Community engagement

Always ensure effective coordination and timely communication among stakeholders."""


class CommunityCoordinationAgent(BaseAIAgent):
    def __init__(self):
        super().__init__(
            agent_name="CommunityCoordinationAgent",
            system_prompt=COMMUNITY_SYSTEM_PROMPT,
            model="gpt-4-turbo-preview",
            temperature=0.3,
        )
        self.stakeholders: List[Dict[str, Any]] = []
        self.connections: List[Dict[str, Any]] = []
        self.meetings: List[Dict[str, Any]] = []
        self.notifications: List[Dict[str, Any]] = []

    def register_stakeholder(
        self,
        stakeholder_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        stakeholder = {
            "id": stakeholder_data.get("id") or str(uuid.uuid4()),
            "name": stakeholder_data.get("name"),
            "type": stakeholder_data.get("type"),
            "department": stakeholder_data.get("department"),
            "role": stakeholder_data.get("role"),
            "contact": stakeholder_data.get("contact"),
            "district_id": stakeholder_data.get("district_id"),
            "block_id": stakeholder_data.get("block_id"),
            "registered_at": datetime.utcnow().isoformat()
        }
        
        self.stakeholders.append(stakeholder)
        return stakeholder

    def create_connection(
        self,
        stakeholder_1_id: str,
        stakeholder_2_id: str,
        connection_type: str,
        strength: float = 0.5
    ) -> Dict[str, Any]:
        connection = {
            "id": f"conn-{len(self.connections) + 1}",
            "source": stakeholder_1_id,
            "target": stakeholder_2_id,
            "type": connection_type,
            "strength": strength,
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.connections.append(connection)
        return connection

    def get_stakeholder_network(
        self,
        stakeholder_id: Optional[str] = None,
        district_id: Optional[int] = None
    ) -> Dict[str, Any]:
        filtered_stakeholders = self.stakeholders
        filtered_connections = self.connections
        
        if stakeholder_id:
            connected_ids = set([stakeholder_id])
            for conn in self.connections:
                if conn["source"] == stakeholder_id:
                    connected_ids.add(conn["target"])
                if conn["target"] == stakeholder_id:
                    connected_ids.add(conn["source"])
            
            filtered_stakeholders = [
                s for s in self.stakeholders
                if s["id"] in connected_ids
            ]
            filtered_connections = [
                c for c in self.connections
                if c["source"] in connected_ids and c["target"] in connected_ids
            ]
        
        if district_id:
            filtered_stakeholders = [
                s for s in filtered_stakeholders
                if s.get("district_id") == district_id
            ]
            stakeholder_ids = {s["id"] for s in filtered_stakeholders}
            filtered_connections = [
                c for c in filtered_connections
                if c["source"] in stakeholder_ids and c["target"] in stakeholder_ids
            ]
        
        return {
            "stakeholders": filtered_stakeholders,
            "connections": filtered_connections,
            "stats": {
                "total_stakeholders": len(filtered_stakeholders),
                "total_connections": len(filtered_connections),
                "average_connections": len(filtered_connections) * 2 / len(filtered_stakeholders) if filtered_stakeholders else 0
            }
        }

    async def schedule_meeting(
        self,
        meeting_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        meeting = {
            "id": f"meet-{len(self.meetings) + 1}",
            "title": meeting_data.get("title"),
            "description": meeting_data.get("description"),
            "scheduled_at": meeting_data.get("scheduled_at"),
            "duration_minutes": meeting_data.get("duration_minutes", 60),
            "location": meeting_data.get("location"),
            "meeting_type": meeting_data.get("meeting_type", "in_person"),
            "organizer_id": meeting_data.get("organizer_id"),
            "attendees": meeting_data.get("attendees", []),
            "agenda": meeting_data.get("agenda", []),
            "status": MeetingStatus.SCHEDULED.value,
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.meetings.append(meeting)
        
        for attendee_id in meeting.get("attendees", []):
            await self.send_notification(
                recipient_id=attendee_id,
                notification_type=NotificationType.MEETING_INVITE.value,
                title=f"Meeting Invite: {meeting['title']}",
                content=f"You have been invited to a meeting scheduled for {meeting['scheduled_at']}",
                reference_id=meeting["id"]
            )
        
        return meeting

    async def send_notification(
        self,
        recipient_id: str,
        notification_type: str,
        title: str,
        content: str,
        reference_id: Optional[str] = None,
        priority: str = "normal"
    ) -> Dict[str, Any]:
        notification = {
            "id": f"notif-{len(self.notifications) + 1}",
            "recipient_id": recipient_id,
            "type": notification_type,
            "title": title,
            "content": content,
            "priority": priority,
            "reference_id": reference_id,
            "read": False,
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.notifications.append(notification)
        logger.info(f"Notification sent: {notification['id']} to {recipient_id}")
        
        return notification

    def get_notifications(
        self,
        recipient_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        filtered = [
            n for n in self.notifications
            if n.get("recipient_id") == recipient_id
        ]
        
        if unread_only:
            filtered = [n for n in filtered if not n.get("read")]
        
        return sorted(filtered, key=lambda x: x["created_at"], reverse=True)[:limit]

    def mark_notification_read(
        self,
        notification_id: str
    ) -> Optional[Dict[str, Any]]:
        for notification in self.notifications:
            if notification["id"] == notification_id:
                notification["read"] = True
                notification["read_at"] = datetime.utcnow().isoformat()
                return notification
        return None

    def get_upcoming_meetings(
        self,
        stakeholder_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        now = datetime.utcnow().isoformat()
        
        upcoming = [
            m for m in self.meetings
            if m.get("scheduled_at", "") >= now
            and m.get("status") == MeetingStatus.SCHEDULED.value
            and (stakeholder_id in m.get("attendees", []) or m.get("organizer_id") == stakeholder_id)
        ]
        
        return sorted(upcoming, key=lambda x: x["scheduled_at"])[:limit]

    async def analyze(self, data: Dict[str, Any]) -> AgentResponse:
        network = self.get_stakeholder_network(
            stakeholder_id=data.get("stakeholder_id"),
            district_id=data.get("district_id")
        )
        return AgentResponse(
            success=True,
            content=network,
            agent_name=self.agent_name
        )

    async def get_recommendations(self, data: Dict[str, Any]) -> AgentResponse:
        meetings = self.get_upcoming_meetings(
            stakeholder_id=data.get("stakeholder_id", ""),
            limit=data.get("limit", 10)
        )
        return AgentResponse(
            success=True,
            content={"recommended_meetings": meetings},
            agent_name=self.agent_name
        )


community_coordination_agent = CommunityCoordinationAgent()
