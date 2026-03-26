from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from ...database import get_db
from ...services.auth import get_current_user
from ...models import User
from ...services.ai.agents.compliance_audit import compliance_audit_agent

router = APIRouter()


class AuditLogCreate(BaseModel):
    user_id: int
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None


@router.get("/report")
async def generate_compliance_report(
    district_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    report = await compliance_audit_agent.generate_compliance_report(
        district_id=district_id,
        start_date=start_date,
        end_date=end_date
    )
    return report


@router.get("/audit-log")
async def get_audit_logs(
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logs = compliance_audit_agent.get_audit_logs(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        limit=limit,
        offset=offset
    )
    return {"logs": logs, "total": len(logs)}


@router.get("/score")
async def get_compliance_score(
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    score = await compliance_audit_agent.calculate_compliance_score(
        entity_type=entity_type,
        entity_id=entity_id
    )
    return score


@router.post("/log")
async def log_action(
    audit_log: AuditLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    log_entry = compliance_audit_agent.log_action(
        user_id=audit_log.user_id,
        action=audit_log.action,
        entity_type=audit_log.entity_type,
        entity_id=audit_log.entity_id,
        details=audit_log.details,
        ip_address=audit_log.ip_address
    )
    return {"message": "Audit log created successfully", "log": log_entry}


@router.get("/status")
async def get_compliance_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    status = compliance_audit_agent.get_compliance_status()
    return status
