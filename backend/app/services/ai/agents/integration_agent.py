from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import json

from ..base_agent import BaseAIAgent, AgentResponse
from ..openai_client import OpenAIClient
from ....utils.logger import get_logger

logger = get_logger(__name__)


class IntegrationType(str, Enum):
    POSHAN_TRACKER = "poshan_tracker"
    ICDS_CAS = "icds_cas"
    WEATHER = "weather"
    ROAD_INFRASTRUCTURE = "road_infrastructure"
    GRIEVANCE_PORTAL = "grievance_portal"
    FINANCE = "finance"
    HRMS = "hrms"


class SyncStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


INTEGRATION_SYSTEM_PROMPT = """You are the Integration Agent for the Ooumph SHAKTI supply chain management system.
Your role is to manage integrations with external government systems, handle data transformations, and coordinate sync operations.

You have expertise in:
- API integration patterns
- Data transformation and mapping
- Error handling and retry logic
- Sync scheduling
- Data validation

Always ensure data integrity and handle integration errors gracefully."""


class IntegrationAgent(BaseAIAgent):
    def __init__(self):
        super().__init__(
            agent_name="IntegrationAgent",
            system_prompt=INTEGRATION_SYSTEM_PROMPT,
            model="gpt-4-turbo-preview",
            temperature=0.2,
        )
        self.sync_queue: List[Dict[str, Any]] = []
        self.integration_configs: Dict[str, Dict[str, Any]] = {}
        self._init_configs()

    def _init_configs(self):
        self.integration_configs = {
            IntegrationType.POSHAN_TRACKER.value: {
                "name": "POSHAN Tracker",
                "base_url": "https://poshan.abdm.gov.in/api",
                "enabled": True,
                "sync_interval_minutes": 60
            },
            IntegrationType.ICDS_CAS.value: {
                "name": "ICDS-CAS",
                "base_url": "https://icds-cas.gov.in/api",
                "enabled": True,
                "sync_interval_minutes": 120
            },
            IntegrationType.WEATHER.value: {
                "name": "Weather Service",
                "base_url": "https://mausam.imd.gov.in/api",
                "enabled": True,
                "sync_interval_minutes": 30
            },
            IntegrationType.ROAD_INFRASTRUCTURE.value: {
                "name": "Road Infrastructure",
                "base_url": "https://nhai.gov.in/api",
                "enabled": True,
                "sync_interval_minutes": 1440
            },
            IntegrationType.GRIEVANCE_PORTAL.value: {
                "name": "Grievance Portal",
                "base_url": "https://pgportal.gov.in/api",
                "enabled": True,
                "sync_interval_minutes": 30
            }
        }

    async def sync_data(
        self,
        integration_type: str,
        data: Dict[str, Any],
        direction: str = "outbound"
    ) -> Dict[str, Any]:
        sync_record = {
            "id": f"sync-{len(self.sync_queue) + 1}",
            "integration_type": integration_type,
            "direction": direction,
            "data": data,
            "status": SyncStatus.PENDING.value,
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.sync_queue.append(sync_record)
        
        try:
            sync_record["status"] = SyncStatus.IN_PROGRESS.value
            
            transformed_data = await self.transform_data(integration_type, data, direction)
            
            sync_record["transformed_data"] = transformed_data
            sync_record["status"] = SyncStatus.COMPLETED.value
            sync_record["completed_at"] = datetime.utcnow().isoformat()
            
            return {
                "success": True,
                "sync_id": sync_record["id"],
                "status": sync_record["status"],
                "data": transformed_data
            }
            
        except Exception as e:
            sync_record["status"] = SyncStatus.FAILED.value
            sync_record["error"] = str(e)
            sync_record["failed_at"] = datetime.utcnow().isoformat()
            
            logger.error(f"Sync failed for {integration_type}: {e}")
            
            return {
                "success": False,
                "sync_id": sync_record["id"],
                "status": sync_record["status"],
                "error": str(e)
            }

    async def transform_data(
        self,
        integration_type: str,
        data: Dict[str, Any],
        direction: str
    ) -> Dict[str, Any]:
        prompt = f"""
Transform the following data for {integration_type} integration.

Direction: {direction}
Source Data:
{json.dumps(data, indent=2)}

Please provide the transformed data in JSON format with:
1. mapped_fields: Field mapping from source to target
2. transformed_data: The transformed data object
3. validation_errors: Any validation errors found
4. warnings: Any warnings or notes
"""

        response = await self.process_async(
            user_input=prompt,
            response_format={"type": "json_object"}
        )

        if response.success:
            return response.content.get("transformed_data", data)
        else:
            logger.warning(f"Data transformation used fallback: {response.error}")
            return data

    def get_sync_status(
        self,
        sync_id: str
    ) -> Optional[Dict[str, Any]]:
        for sync in self.sync_queue:
            if sync["id"] == sync_id:
                return sync
        return None

    def get_pending_syncs(
        self,
        integration_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        pending = [
            sync for sync in self.sync_queue
            if sync["status"] in [SyncStatus.PENDING.value, SyncStatus.FAILED.value]
        ]
        
        if integration_type:
            pending = [
                sync for sync in pending
                if sync["integration_type"] == integration_type
            ]
        
        return pending

    def get_integration_config(
        self,
        integration_type: str
    ) -> Optional[Dict[str, Any]]:
        return self.integration_configs.get(integration_type)

    def get_all_integrations(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": type_key,
                **config,
                "last_sync": self._get_last_sync(type_key)
            }
            for type_key, config in self.integration_configs.items()
        ]

    def _get_last_sync(self, integration_type: str) -> Optional[Dict[str, Any]]:
        for sync in reversed(self.sync_queue):
            if sync["integration_type"] == integration_type:
                return {
                    "sync_id": sync["id"],
                    "status": sync["status"],
                    "timestamp": sync.get("completed_at") or sync.get("created_at")
                }
        return None

    async def retry_failed_sync(
        self,
        sync_id: str
    ) -> Dict[str, Any]:
        sync_record = self.get_sync_status(sync_id)
        
        if not sync_record:
            return {"success": False, "error": "Sync record not found"}
        
        if sync_record["status"] != SyncStatus.FAILED.value:
            return {"success": False, "error": "Sync is not in failed state"}
        
        return await self.sync_data(
            integration_type=sync_record["integration_type"],
            data=sync_record["data"],
            direction=sync_record["direction"]
        )

    async def analyze(self, data: Dict[str, Any]) -> AgentResponse:
        result = await self.sync_data(
            integration_type=data.get("integration_type"),
            data=data.get("data", {}),
            direction=data.get("direction", "outbound")
        )
        return AgentResponse(
            success=result.get("success", False),
            content=result,
            agent_name=self.agent_name
        )

    async def get_recommendations(self, data: Dict[str, Any]) -> AgentResponse:
        pending = self.get_pending_syncs(integration_type=data.get("integration_type"))
        return AgentResponse(
            success=True,
            content={"pending_syncs": pending, "count": len(pending)},
            agent_name=self.agent_name
        )


integration_agent = IntegrationAgent()
