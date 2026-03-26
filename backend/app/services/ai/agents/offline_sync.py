from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import uuid

from ..base_agent import BaseAIAgent, AgentResponse
from ..openai_client import OpenAIClient
from ....utils.logger import get_logger

logger = get_logger(__name__)


class SyncStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"


class ConflictResolutionStrategy(str, Enum):
    SERVER_WINS = "server_wins"
    CLIENT_WINS = "client_wins"
    MANUAL_MERGE = "manual_merge"


OFFLINE_SYNC_SYSTEM_PROMPT = """You are the Offline Sync Agent (OSA) for the Ooumph SHAKTI supply chain management system.
Your role is to manage offline data synchronization, detect conflicts, and provide intelligent resolution strategies.

You have expertise in:
- Data synchronization patterns
- Conflict detection and resolution
- Offline-first architecture
- Data integrity validation
- State reconciliation

Always prioritize data integrity and provide clear resolution paths for conflicts."""


class OfflineSyncAgent(BaseAIAgent):
    def __init__(self):
        super().__init__(
            agent_name="OfflineSyncAgent",
            system_prompt=OFFLINE_SYNC_SYSTEM_PROMPT,
            model="gpt-4-turbo-preview",
            temperature=0.2,
        )
        self.pending_syncs: List[Dict[str, Any]] = []
        self.conflicts: List[Dict[str, Any]] = []

    async def process_sync(
        self,
        sync_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        sync_id = str(uuid.uuid4())
        sync_record = {
            "sync_id": sync_id,
            "entity_type": sync_data.get("entity_type"),
            "entity_id": sync_data.get("entity_id"),
            "action": sync_data.get("action"),
            "data": sync_data.get("data"),
            "timestamp": sync_data.get("timestamp", datetime.utcnow().isoformat()),
            "device_id": sync_data.get("device_id"),
            "status": SyncStatus.PENDING.value,
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.pending_syncs.append(sync_record)
        
        return {
            "sync_id": sync_id,
            "status": SyncStatus.PENDING.value,
            "message": "Sync data queued for processing"
        }

    async def detect_conflicts(
        self,
        client_data: Dict[str, Any],
        server_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        conflicts = []
        
        for key in set(list(client_data.keys()) + list(server_data.keys())):
            client_value = client_data.get(key)
            server_value = server_data.get(key)
            
            if client_value != server_value and client_value is not None and server_value is not None:
                conflicts.append({
                    "field": key,
                    "client_value": client_value,
                    "server_value": server_value
                })
        
        return {
            "has_conflicts": len(conflicts) > 0,
            "conflicts": conflicts,
            "conflict_count": len(conflicts)
        }

    async def resolve_conflict(
        self,
        conflict_data: Dict[str, Any],
        strategy: ConflictResolutionStrategy
    ) -> Dict[str, Any]:
        resolution = {
            "strategy_used": strategy.value,
            "resolved_at": datetime.utcnow().isoformat(),
            "resolved_data": {}
        }
        
        if strategy == ConflictResolutionStrategy.SERVER_WINS:
            resolution["resolved_data"] = conflict_data.get("server_data", {})
            resolution["message"] = "Server data preserved"
            
        elif strategy == ConflictResolutionStrategy.CLIENT_WINS:
            resolution["resolved_data"] = conflict_data.get("client_data", {})
            resolution["message"] = "Client data preserved"
            
        elif strategy == ConflictResolutionStrategy.MANUAL_MERGE:
            prompt = f"""
Analyze the following conflict and suggest a merged resolution.

Conflict Details:
{conflict_data}

Please provide a merged solution that:
1. Preserves critical data from both sources
2. Maintains data integrity
3. Provides clear reasoning for the merge

Response in JSON format with:
1. merged_data: The merged data object
2. reasoning: Explanation of merge decisions
3. confidence: Confidence level (0-1)
"""
            response = await self.process_async(
                user_input=prompt,
                response_format={"type": "json_object"}
            )
            
            if response.success:
                resolution["resolved_data"] = response.content.get("merged_data", {})
                resolution["reasoning"] = response.content.get("reasoning", "")
                resolution["confidence"] = response.content.get("confidence", 0.5)
                resolution["message"] = "Conflict resolved through intelligent merge"
            else:
                resolution["resolved_data"] = conflict_data.get("server_data", {})
                resolution["message"] = "Fallback to server data due to merge failure"
        
        return resolution

    async def get_pending_syncs(
        self,
        device_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if device_id:
            return [s for s in self.pending_syncs if s.get("device_id") == device_id]
        return self.pending_syncs

    async def get_sync_status(
        self,
        sync_id: str
    ) -> Dict[str, Any]:
        for sync in self.pending_syncs:
            if sync.get("sync_id") == sync_id:
                return sync
        return {"error": "Sync record not found", "sync_id": sync_id}

    async def mark_sync_complete(
        self,
        sync_id: str,
        status: SyncStatus = SyncStatus.COMPLETED
    ) -> Dict[str, Any]:
        for sync in self.pending_syncs:
            if sync.get("sync_id") == sync_id:
                sync["status"] = status.value
                sync["completed_at"] = datetime.utcnow().isoformat()
                return {"message": f"Sync {sync_id} marked as {status.value}"}
        return {"error": "Sync record not found", "sync_id": sync_id}

    async def get_conflicts(
        self,
        entity_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if entity_type:
            return [c for c in self.conflicts if c.get("entity_type") == entity_type]
        return self.conflicts

    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.detect_conflicts(
            client_data=data.get("client_data", {}),
            server_data=data.get("server_data", {})
        )

    async def get_recommendations(self, conflict_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.resolve_conflict(
            conflict_data=conflict_data,
            strategy=ConflictResolutionStrategy.MANUAL_MERGE
        )


offline_sync_agent = OfflineSyncAgent()
