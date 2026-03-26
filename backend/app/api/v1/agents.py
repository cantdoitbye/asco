from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from ...database import get_db
from ...services.auth import get_current_user
from ...models import User
from ...services.ai.openai_client import openai_client
from ...services.ai.agents.route_intelligence import RouteIntelligenceAgent
from ...services.ai.agents.supply_sentinel import SupplySentinelAgent
from ...services.ai.agents.demand_forecast import DemandForecastingAgent
from ...services.stubs.weather_service import weather_service_stub
from ...services.stubs.road_infrastructure import road_infrastructure_stub

from ...services.stubs.poshan_tracker import poshan_tracker_stub

from ...services.stubs.icds_cas import icds_cas_stub

from datetime import datetime

router = APIRouter()


prefix = "/agents"


class RouteOptimizeRequest(BaseModel):
    warehouse_id: int
    anganwadi_center_ids: List[int]
    vehicle_capacity_kg: float
    priority: str = "balanced"


class RouteAnalysisRequest(BaseModel):
    route_id: int
    include_weather: bool = True
    include_road_conditions: bool = True


class SupplyMonitorRequest(BaseModel):
    district_id: Optional[int] = None
    block_id: Optional[int] = None
    threshold_low: float = 20.0
    threshold_high: float = 80.0


class ForecastRequest(BaseModel):
    district_id: Optional[int] = None
    block_id: Optional[int] = None
    village_id: Optional[int] = None
    forecast_days: int = 7
    include_seasonality: bool = True


class RouteOptimizeResponse(BaseModel):
    optimized_routes: List[Dict[str, Any]]
    total_distance_km: float
    estimated_time_minutes: int
    recommendations: List[str]


class SupplyAlert(BaseModel):
    id: str
    type: str
    severity: str
    message: str
    entity_type: str
    entity_id: int
    timestamp: datetime
    acknowledged: bool = False


class DemandForecastResponse(BaseModel):
    forecasts: List[Dict[str, Any]]
    confidence_level: float
    seasonal_adjustment: Optional[float]
    recommendations: List[str]


@router.post("/route/optimize")
async def optimize_route(
    request: RouteOptimizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from ...models import AnganwadiCenter, Warehouse, Route
    
    warehouse = db.query(Warehouse).filter(Warehouse.id == request.warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    centers = db.query(AnganwadiCenter).filter(
        AnganwadiCenter.id.in_(request.anganwadi_center_ids)
    ).all()
    
    center_data = [
        {
            "id": c.id,
            "name": c.name,
            "latitude": float(c.latitude) if c.latitude else 0.0,
            "longitude": float(c.longitude) if c.longitude else 1.0,
            "demand": c.total_beneficiaries
        }
        for c in centers
    ]
    
    weather_data = await weather_service_stub.get_current_weather(
        float(warehouse.latitude) if warehouse.latitude else 1.0,
        float(warehouse.longitude) if warehouse.longitude else 1.0
    )
    
    agent = RouteIntelligenceAgent()
    result = await agent.optimize_route(
        warehouse_data={
            "id": warehouse.id,
            "name": warehouse.name,
            "latitude": float(warehouse.latitude) if warehouse.latitude else 1.0,
            "longitude": float(warehouse.longitude) if warehouse.longitude else 1.0
        },
        delivery_points=center_data,
        vehicle_capacity=request.vehicle_capacity_kg,
        weather_conditions=weather_data.get("current", {}),
        priority=request.priority
 )
    
    return result


@router.post("/route/analyze")
async def analyze_route(
    request: RouteAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    from ...models import Route, AnganwadiCenter, Warehouse
    
    route = db.query(Route).filter(Route.id == request.route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    weather_data = None
    if request.include_weather:
        warehouse = db.query(Warehouse).filter(Warehouse.id == route.warehouse_id).first()
        if warehouse and warehouse.latitude and warehouse.longitude:
            weather_data = await weather_service_stub.get_current_weather(
                float(warehouse.latitude),
                float(warehouse.longitude)
            )
    
    road_data = None
    if request.include_road_conditions:
        road_data = await road_infrastructure_stub.get_road_conditions(f"route_{route.id}")
    
    agent = RouteIntelligenceAgent()
    result = await agent.analyze_route_conditions(
        route_data={
            "id": route.id,
            "name": route.name,
            "total_distance_km": float(route.total_distance_km) if route.total_distance_km else 0,
            "stops_count": route.stops_count
        },
        weather_conditions=weather_data,
        road_conditions=road_data
    )
    
    return result


@router.get("/supply/monitor")
async def monitor_supply(
    district_id: Optional[int] = Query(None),
    block_id: Optional[int] = Query(None),
    threshold_low: float = Query(20.0),
    threshold_high: float = Query(80.0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from ...models import Inventory, AnganwadiCenter, Village, Block
    
    query = db.query(Inventory).join(
        AnganwadiCenter, Inventory.anganwadi_center_id == AnganwadiCenter.id
    ).join(
        Village, AnganwadiCenter.village_id == Village.id
    )
    
    if block_id:
        query = query.filter(Village.block_id == block_id)
    elif district_id:
        query = query.join(Block).filter(Block.district_id == district_id)
    
    inventory_items = query.all()
    
    agent = SupplySentinelAgent()
    result = await agent.monitor_inventory(
        inventory_data=[
            {
                "id": item.id,
                "item_id": item.item_id,
                "quantity": float(item.quantity) if item.quantity else 0,
                "min_threshold": float(item.min_threshold) if item.min_threshold else 0,
                "max_threshold": float(item.max_threshold) if item.max_threshold else 0,
                "center_id": item.anganwadi_center_id,
                "center_name": item.AnganwadiCenter.name if hasattr(item, 'AnganwadiCenter') else "Unknown"
            }
            for item in inventory_items
        ],
        thresholds={"low": threshold_low, "high": threshold_high}
    )
    
    return result


@router.get("/supply/alerts")
async def get_supply_alerts(
    district_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from ...models import Inventory, AnganwadiCenter
    
    query = db.query(Inventory).join(
        AnganwadiCenter, Inventory.anganwadi_center_id == AnganwadiCenter.id
    )
    
    inventory_items = query.filter(
        Inventory.quantity <= Inventory.min_threshold
    ).all()
    
    alerts = []
    for item in inventory_items:
        alerts.append({
            "id": f"alert_{item.id}",
            "type": "low_stock",
            "severity": "high" if item.quantity <= item.min_threshold * 0.5 else "medium",
            "message": f"Low stock at {item.AnganwadiCenter.name}: {item.quantity} units remaining",
            "entity_type": "inventory",
            "entity_id": item.id,
            "timestamp": datetime.utcnow(),
            "acknowledged": False
        })
    
    return {"alerts": alerts, "total": len(alerts)}


@router.get("/supply/disruptions")
async def get_disruptions(
    district_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    weather_alerts = []
    road_issues = []
    
    if district_id:
        weather_alerts_data = await weather_service_stub.get_weather_alerts(district_id)
        weather_alerts = weather_alerts_data.get("alerts", [])
        
        road_closures = await road_infrastructure_stub.get_road_closures(district_id)
        road_issues = road_closures.get("active_closures", [])
    
    disruptions = []
    for alert in weather_alerts:
        disruptions.append({
            "type": "weather",
            "severity": alert.get("severity", "moderate"),
            "description": alert.get("description", "Weather alert"),
            "affected_area": f"District {district_id}",
            "timestamp": datetime.utcnow()
        })
    
    for closure in road_issues:
        disruptions.append({
            "type": "road_closure",
            "severity": "high",
            "description": f"Road closed: {closure.get('road_name', 'Unknown')} - {closure.get('reason', 'Unknown reason')}",
            "affected_area": f"District {district_id}",
            "timestamp": datetime.utcnow()
        })
    
    return {"disruptions": disruptions, "total": len(disruptions)}


@router.post("/forecast/generate")
async def generate_forecast(
    request: ForecastRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from ...models import AnganwadiCenter, Village, Block
    from sqlalchemy import func
    
    query = db.query(
        AnganwadiCenter.total_beneficiaries,
        AnganwadiCenter.children_0_3,
        AnganwadiCenter.children_3_6,
        AnganwadiCenter.pregnant_women,
        AnganwadiCenter.lactating_mothers
    ).join(
        Village, AnganwadiCenter.village_id == Village.id
    )
    
    if request.village_id:
        query = query.filter(Village.id == request.village_id)
    elif request.block_id:
        query = query.filter(Village.block_id == request.block_id)
    elif request.district_id:
        query = query.join(Block).filter(Block.district_id == request.district_id)
    
    historical_data = [
        {
            "total_beneficiaries": r[0] or 0,
            "children_0_3": r[1] or 0,
            "children_3_6": r[2] or 0,
            "pregnant_women": r[3] or 0,
            "lactating_mothers": r[4] or 1
        }
        for r in query.all()
    ]
    
    agent = DemandForecastingAgent()
    result = await agent.generate_forecast(
        historical_data=historical_data,
        forecast_days=request.forecast_days,
        include_seasonality=request.include_seasonality
    )
    
    return result


@router.get("/forecast/village/{village_id}")
async def get_village_forecast(
    village_id: int,
    forecast_days: int = Query(7),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from ...models import AnganwadiCenter, Village
    
    village = db.query(Village).filter(Village.id == village_id).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")
    
    centers = db.query(AnganwadiCenter).filter(
        AnganwadiCenter.village_id == village_id
    ).all()
    
    historical_data = [
        {
            "total_beneficiaries": c.total_beneficiaries,
            "children_0_3": c.children_0_3,
            "children_3_6": c.children_3_6,
            "pregnant_women": c.pregnant_women,
            "lactating_mothers": c.lactating_mothers
        }
        for c in centers
    ]
    
    agent = DemandForecastingAgent()
    result = await agent.generate_forecast(
        historical_data=historical_data,
        forecast_days=forecast_days,
        include_seasonality=True
    )
    
    result["village_id"] = village_id
    result["village_name"] = village.name
    return result


@router.get("/forecast/block/{block_id}")
async def get_block_forecast(
    block_id: int,
    forecast_days: int = Query(7),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from ...models import AnganwadiCenter, Village, Block
    
    block = db.query(Block).filter(Block.id == block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    
    centers = db.query(AnganwadiCenter).join(
        Village, AnganwadiCenter.village_id == Village.id
    ).filter(Village.block_id == block_id).all()
    
    historical_data = [
        {
            "total_beneficiaries": c.total_beneficiaries,
            "children_0_3": c.children_0_3,
            "children_3_6": c.children_3_6,
            "pregnant_women": c.pregnant_women,
            "lactating_mothers": c.lactating_mothers
        }
        for c in centers
    ]
    
    agent = DemandForecastingAgent()
    result = await agent.generate_forecast(
        historical_data=historical_data,
        forecast_days=forecast_days,
        include_seasonality=True
    )
    
    result["block_id"] = block_id
    result["block_name"] = block.name
    return result
