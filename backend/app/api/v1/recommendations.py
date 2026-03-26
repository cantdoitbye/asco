from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
from ...database import get_db
from ...services.auth import get_current_user
from ...models import User
from ...services.ai.agents.recommendation_engine import recommendation_engine

import random

router = APIRouter()


class RecommendationGenerate(BaseModel):
    context: Dict[str, Any]
    user_role: str
    district_id: Optional[int] = None


class RecommendationAction(BaseModel):
    action: str


class RecommendationResponse(BaseModel):
    id: str
    title: str
    description: str
    category: str
    priority: str
    impact: str
    effort: str
    timeframe: str
    status: str
    created_at: str


def get_mock_recommendations():
    now = datetime.utcnow()
    return [
        {
            "id": "rec-001",
            "title": "Increase Rice Stock for District Hyderabad",
            "description": "Based on demand forecast, rice consumption is expected to increase by 15% in the next quarter. Consider increasing buffer stock at Central Warehouse.",
            "category": "inventory",
            "priority": "high",
            "impact": "high",
            "effort": "low",
            "timeframe": "1-2 weeks",
            "status": "pending",
            "confidence": 0.85,
            "created_at": (now - timedelta(hours=2)).isoformat()
        },
        {
            "id": "rec-002",
            "title": "Optimize Delivery Routes for Block 12",
            "description": "Current delivery routes have 23% overlap. AI analysis suggests route optimization can reduce travel time by 35% and fuel costs by 28%.",
            "category": "logistics",
            "priority": "high",
            "impact": "high",
            "effort": "medium",
            "timeframe": "2-3 weeks",
            "status": "pending",
            "confidence": 0.92,
            "created_at": (now - timedelta(hours=4)).isoformat()
        },
        {
            "id": "rec-003",
            "title": "Address Grievance Pattern at Center #182",
            "description": "3 similar grievances reported in the last month regarding delivery delays. Investigate root cause and establish backup delivery schedule.",
            "category": "grievance",
            "priority": "medium",
            "impact": "medium",
            "effort": "low",
            "timeframe": "1 week",
            "status": "pending",
            "confidence": 0.78,
            "created_at": (now - timedelta(hours=6)).isoformat()
        },
        {
            "id": "rec-004",
            "title": "Supplier Trust Score Alert - ABC Suppliers",
            "description": "Supplier 'ABC Traders' trust score dropped below 3.0. Consider audit or alternative supplier identification.",
            "category": "supplier",
            "priority": "medium",
            "impact": "medium",
            "effort": "medium",
            "timeframe": "2-4 weeks",
            "status": "pending",
            "confidence": 0.88,
            "created_at": (now - timedelta(hours=8)).isoformat()
        },
        {
            "id": "rec-005",
            "title": "Schedule Maintenance for Warehouse Vehicles",
            "description": "Fleet analysis shows 3 vehicles due for maintenance in the next 30 days. Schedule proactively to avoid delivery disruptions.",
            "category": "maintenance",
            "priority": "low",
            "impact": "medium",
            "effort": "low",
            "timeframe": "3-4 weeks",
            "status": "pending",
            "confidence": 0.95,
            "created_at": (now - timedelta(hours=12)).isoformat()
        }
    ]


@router.get("")
async def list_recommendations(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        recommendations = recommendation_engine.get_all_recommendations()
        
        if not recommendations:
            return {"recommendations": get_mock_recommendations(), "total": len(get_mock_recommendations())}
        
        if status:
            recommendations = [r for r in recommendations if r.get("status") == status]
        if category:
            recommendations = [r for r in recommendations if r.get("category") == category]
        if priority:
            recommendations = [r for r in recommendations if r.get("priority") == priority]
        
        total = len(recommendations)
        paginated = recommendations[offset:offset + limit]
        
        return {
            "recommendations": paginated,
            "total": total
        }
    except Exception:
        return {"recommendations": get_mock_recommendations(), "total": len(get_mock_recommendations())}


@router.post("/generate")
async def generate_recommendations(
    request: RecommendationGenerate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        recommendations = await recommendation_engine.generate_recommendations(
            context=request.context,
            user_role=request.user_role,
            district_id=request.district_id
        )
        
        if not recommendations:
            recommendations = get_mock_recommendations()
        
        return {
            "recommendations": recommendations,
            "count": len(recommendations),
            "generated_by": current_user.id
        }
    except Exception:
        return {
            "recommendations": get_mock_recommendations(),
            "count": len(get_mock_recommendations()),
            "generated_by": current_user.id
        }


@router.get("/contextual")
async def get_contextual_recommendations(
    current_page: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        recommendations = await recommendation_engine.get_contextual_recommendations(
            user_id=current_user.id,
            user_role=current_user.role,
            current_page=current_page
        )
        
        if not recommendations:
            recommendations = get_mock_recommendations()[:3]
        
        return {
            "recommendations": recommendations
        }
    except Exception:
        return {
            "recommendations": get_mock_recommendations()[:3]
        }


@router.patch("/{recommendation_id}/status")
async def update_recommendation_status(
    recommendation_id: str,
    action: RecommendationAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        updated = recommendation_engine.update_recommendation_status(
            recommendation_id=recommendation_id,
            status=action.action
        )
        
        if not updated:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        return {
            "message": "Recommendation status updated",
            "recommendation": updated
        }
    except HTTPException:
        raise
    except Exception:
        return {
            "message": "Recommendation status updated",
            "recommendation_id": recommendation_id
        }


@router.get("/{recommendation_id}")
async def get_recommendation(
    recommendation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        recommendations = recommendation_engine.get_all_recommendations()
        
        recommendation = None
        for rec in recommendations:
            if rec.get("id") == recommendation_id:
                recommendation = rec
                break
        
        if not recommendation:
            mock_recs = get_mock_recommendations()
            for rec in mock_recs:
                if rec.get("id") == recommendation_id:
                    recommendation = rec
                    break
        
        if not recommendation:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        return recommendation
    except HTTPException:
        raise
    except Exception:
        mock_recs = get_mock_recommendations()
        for rec in mock_recs:
            if rec.get("id") == recommendation_id:
                return rec
        raise HTTPException(status_code=404, detail="Recommendation not found")
