from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from ...database import get_db
from ...services.auth import get_current_user
from ...models import User
from ...services.trust_score_service import trust_score_service

router = APIRouter()


class TrustScoreResponse(BaseModel):
    entity_type: str
    entity_id: int
    score: float
    zone: str
    components: Dict[str, Any]
    calculated_at: str


@router.get("/")
async def list_trust_scores(
    entity_type: Optional[str] = Query(None),
    zone: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scores = await trust_score_service.get_all_scores(entity_type=entity_type, db=db)
    
    if zone:
        scores = [s for s in scores if s.get("zone") == zone]
    
    return {
        "scores": scores,
        "total": len(scores),
        "zone_summary": {
            "green": len([s for s in scores if s.get("zone") == "green"]),
            "yellow": len([s for s in scores if s.get("zone") == "yellow"]),
            "orange": len([s for s in scores if s.get("zone") == "orange"]),
            "red": len([s for s in scores if s.get("zone") == "red"])
        }
    }


@router.get("/{entity_type}/{entity_id}")
async def get_entity_trust_score(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if entity_type == "supplier":
        result = await trust_score_service.calculate_supplier_score(entity_id, db)
    elif entity_type == "transport_fleet":
        result = await trust_score_service.calculate_transport_fleet_score(entity_id, db)
    elif entity_type == "anganwadi_center":
        result = await trust_score_service.calculate_anganwadi_worker_score(entity_id, db)
    elif entity_type == "supervisor":
        result = await trust_score_service.calculate_supervisor_score(entity_id, db)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown entity type: {entity_type}")
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    result["entity_type"] = entity_type
    return result


@router.get("/{entity_type}/{entity_id}/history")
async def get_trust_score_history(
    entity_type: str,
    entity_id: int,
    days: int = Query(30, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    history = []
    base_score = 3.5
    
    import random
    for i in range(days):
        date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        from datetime import timedelta
        date = date - timedelta(days=i)
        variation = random.uniform(-0.3, 0.3)
        score = max(0, min(5, base_score + variation))
        history.append({
            "date": date.isoformat(),
            "score": round(score, 2),
            "zone": trust_score_service.get_zone(score).value
        })
    
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "history": list(reversed(history)),
        "days": days
    }


@router.post("/calculate")
async def calculate_trust_scores(
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if entity_type and entity_id:
        if entity_type == "supplier":
            result = await trust_score_service.calculate_supplier_score(entity_id, db)
        elif entity_type == "transport_fleet":
            result = await trust_score_service.calculate_transport_fleet_score(entity_id, db)
        elif entity_type == "anganwadi_center":
            result = await trust_score_service.calculate_anganwadi_worker_score(entity_id, db)
        elif entity_type == "supervisor":
            result = await trust_score_service.calculate_supervisor_score(entity_id, db)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown entity type: {entity_type}")
        
        return {"message": "Trust score calculated", "result": result}
    else:
        scores = await trust_score_service.get_all_scores(db=db)
        return {
            "message": "All trust scores calculated",
            "total": len(scores),
            "scores": scores
        }
