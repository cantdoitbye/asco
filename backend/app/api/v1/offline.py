from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from ...database import get_db
from ...services.auth import get_current_user
from ...models import User
from ...services.ai.agents.offline_sync import offline_sync_agent, ConflictResolutionStrategy

router = APIRouter()


class SyncDataRequest(BaseModel):
    entity_type: str
    entity_id: Optional[int] = None
    action: str
    data: Dict[str, Any]
    timestamp: Optional[str] = None
    device_id: str


class ConflictResolutionRequest(BaseModel):
    conflict_id: str
    strategy: str
    client_data: Dict[str, Any]
    server_data: Dict[str, Any]


@router.post("/sync")
async def sync_offline_data(
    sync_request: SyncDataRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await offline_sync_agent.process_sync({
        "entity_type": sync_request.entity_type,
        "entity_id": sync_request.entity_id,
        "action": sync_request.action,
        "data": sync_request.data,
        "timestamp": sync_request.timestamp or datetime.utcnow().isoformat(),
        "device_id": sync_request.device_id
    })
    
    return result


@router.get("/pending")
async def get_pending_syncs(
    device_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pending = await offline_sync_agent.get_pending_syncs(device_id=device_id)
    
    return {
        "pending_syncs": pending,
        "total": len(pending)
    }


@router.get("/status/{sync_id}")
async def get_sync_status(
    sync_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    status = await offline_sync_agent.get_sync_status(sync_id)
    
    if "error" in status:
        raise HTTPException(status_code=404, detail=status["error"])
    
    return status


@router.post("/complete/{sync_id}")
async def complete_sync(
    sync_id: str,
    status: str = Query("completed"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await offline_sync_agent.mark_sync_complete(
        sync_id,
        status=status
    )
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.post("/conflicts/detect")
async def detect_conflicts(
    client_data: Dict[str, Any],
    server_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await offline_sync_agent.detect_conflicts(
        client_data=client_data,
        server_data=server_data
    )
    
    return result


@router.post("/conflicts/resolve")
async def resolve_conflict(
    request: ConflictResolutionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        strategy = ConflictResolutionStrategy(request.strategy)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid strategy. Use: server_wins, client_wins, or manual_merge"
        )
    
    result = await offline_sync_agent.resolve_conflict(
        conflict_data={
            "conflict_id": request.conflict_id,
            "client_data": request.client_data,
            "server_data": request.server_data
        },
        strategy=strategy
    )
    
    return result


@router.get("/conflicts")
async def get_conflicts(
    entity_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conflicts = await offline_sync_agent.get_conflicts(entity_type=entity_type)
    
    return {
        "conflicts": conflicts,
        "total": len(conflicts)
    }
