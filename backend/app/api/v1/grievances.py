from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import uuid
from ...database import get_db
from ...services.auth import get_current_user
from ...models import User, Grievance
from ...services.ai.agents.grievance_intelligence import grievance_intelligence_agent

router = APIRouter()


class GrievanceCreate(BaseModel):
    title: str
    description: str
    category: str
    priority: str = "medium"


class GrievanceUpdate(BaseModel):
    status: Optional[str] = None
    resolution_notes: Optional[str] = None
    priority: Optional[str] = None


class GrievanceResponse(BaseModel):
    id: int
    ticket_number: str
    title: str
    description: str
    category: str
    priority: str
    status: str
    created_at: datetime


@router.get("")
async def list_grievances(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Grievance)
    
    if status:
        query = query.filter(Grievance.status == status)
    if category:
        query = query.filter(Grievance.category == category)
    
    grievances = query.order_by(Grievance.created_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "grievances": [
            {
                "id": g.id,
                "ticket_number": g.ticket_number,
                "title": g.title,
                "description": g.description,
                "category": g.category,
                "priority": g.priority,
                "status": g.status,
                "ai_analysis": g.ai_analysis,
                "sentiment_score": float(g.sentiment_score) if g.sentiment_score else None,
                "created_at": g.created_at.isoformat() if g.created_at else None,
                "resolved_at": g.resolved_at.isoformat() if g.resolved_at else None
            }
            for g in grievances
        ],
        "total": query.count()
    }


@router.post("")
async def create_grievance(
    grievance: GrievanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ticket_number = f"GRV-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    
    new_grievance = Grievance(
        ticket_number=ticket_number,
        submitted_by_id=current_user.id,
        title=grievance.title,
        description=grievance.description,
        category=grievance.category,
        priority=grievance.priority,
        status="open",
        created_at=datetime.utcnow()
    )
    
    db.add(new_grievance)
    db.commit()
    db.refresh(new_grievance)
    
    try:
        analysis = await grievance_intelligence_agent.analyze_grievance({
            "id": new_grievance.id,
            "title": new_grievance.title,
            "description": new_grievance.description,
            "category": new_grievance.category
        })
        
        if "sentiment_score" in analysis:
            new_grievance.sentiment_score = analysis.get("sentiment_score")
            new_grievance.ai_analysis = str(analysis)
            db.commit()
    except Exception:
        pass
    
    return {
        "id": new_grievance.id,
        "ticket_number": new_grievance.ticket_number,
        "title": new_grievance.title,
        "status": new_grievance.status
    }


@router.get("/{grievance_id}")
async def get_grievance(
    grievance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    grievance = db.query(Grievance).filter(Grievance.id == grievance_id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")
    
    return {
        "id": grievance.id,
        "ticket_number": grievance.ticket_number,
        "title": grievance.title,
        "description": grievance.description,
        "category": grievance.category,
        "priority": grievance.priority,
        "status": grievance.status,
        "ai_analysis": grievance.ai_analysis,
        "sentiment_score": float(grievance.sentiment_score) if grievance.sentiment_score else None,
        "resolution_notes": grievance.resolution_notes,
        "created_at": grievance.created_at.isoformat() if grievance.created_at else None,
        "resolved_at": grievance.resolved_at.isoformat() if grievance.resolved_at else None
    }


@router.patch("/{grievance_id}")
async def update_grievance(
    grievance_id: int,
    update_data: GrievanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    grievance = db.query(Grievance).filter(Grievance.id == grievance_id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")
    
    if update_data.status:
        grievance.status = update_data.status
        if update_data.status == "resolved":
            grievance.resolved_at = datetime.utcnow()
    if update_data.resolution_notes:
        grievance.resolution_notes = update_data.resolution_notes
    if update_data.priority:
        grievance.priority = update_data.priority
    
    grievance.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Grievance updated successfully", "id": grievance.id}


@router.post("/{grievance_id}/analyze")
async def analyze_grievance(
    grievance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    grievance = db.query(Grievance).filter(Grievance.id == grievance_id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")
    
    analysis = await grievance_intelligence_agent.analyze_grievance({
        "id": grievance.id,
        "title": grievance.title,
        "description": grievance.description,
        "category": grievance.category
    })
    
    if "sentiment_score" in analysis:
        grievance.sentiment_score = analysis.get("sentiment_score")
        grievance.ai_analysis = str(analysis)
        db.commit()
    
    return {"analysis": analysis, "grievance_id": grievance_id}
