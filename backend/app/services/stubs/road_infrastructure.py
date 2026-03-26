from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random


class RoadInfrastructureStub:
    def __init__(self):
        self.base_url = "https://nhai.gov.in/api/roads/v1"
    
    async def get_road_conditions(self, route_id: str) -> Dict:
        conditions = ["excellent", "good", "fair", "poor", "damaged"]
        condition = random.choice(conditions)
        
        return {
            "route_id": route_id,
            "road_condition": condition,
            "condition_score": round(random.uniform(1, 10), 1),
            "surface_type": random.choice(["asphalt", "concrete", "gravel", "mixed"]),
            "lanes": random.choice([2, 4, 6]),
            "shoulder_condition": random.choice(["good", "fair", "poor"]),
            "last_inspection": (datetime.utcnow() - timedelta(days=random.randint(1, 90))).isoformat(),
            "next_inspection": (datetime.utcnow() + timedelta(days=random.randint(1, 90))).isoformat(),
            "data_source": "ROAD_INFRA_STUB"
        }
    
    async def get_route_details(self, origin_lat: float, origin_lon: float, 
                                 dest_lat: float, dest_lon: float) -> Dict:
        distance = round(random.uniform(10, 200), 1)
        avg_speed = random.randint(30, 60)
        estimated_time = round(distance / avg_speed * 60, 0)
        
        return {
            "origin": {"latitude": origin_lat, "longitude": origin_lon},
            "destination": {"latitude": dest_lat, "longitude": dest_lon},
            "distance_km": distance,
            "estimated_time_minutes": int(estimated_time),
            "route_type": random.choice(["highway", "state_highway", "district_road", "village_road"]),
            "toll_required": random.choice([True, False]),
            "toll_amount": round(random.uniform(0, 200), 0) if random.choice([True, False]) else 0,
            "waypoints": self._generate_waypoints(origin_lat, origin_lon, dest_lat, dest_lon),
            "data_source": "ROAD_INFRA_STUB"
        }
    
    def _generate_waypoints(self, o_lat: float, o_lon: float, d_lat: float, d_lon: float) -> List[Dict]:
        waypoints = []
        num_waypoints = random.randint(2, 5)
        
        for i in range(num_waypoints):
            ratio = (i + 1) / (num_waypoints + 1)
            lat = o_lat + (d_lat - o_lat) * ratio + random.uniform(-0.05, 0.05)
            lon = o_lon + (d_lon - o_lon) * ratio + random.uniform(-0.05, 0.05)
            waypoints.append({
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
                "name": f"Point_{i+1}",
                "type": random.choice(["junction", "village", "landmark"])
            })
        
        return waypoints
    
    async def get_traffic_conditions(self, route_id: str) -> Dict:
        congestion_levels = ["free", "light", "moderate", "heavy", "congested"]
        
        return {
            "route_id": route_id,
            "current_congestion": random.choice(congestion_levels),
            "average_speed_kmh": round(random.uniform(20, 70), 1),
            "delay_minutes": random.randint(0, 45),
            "incidents": self._generate_incidents(),
            "last_updated": datetime.utcnow().isoformat(),
            "data_source": "ROAD_INFRA_STUB"
        }
    
    def _generate_incidents(self) -> List[Dict]:
        incidents = []
        if random.random() > 0.7:
            incident_types = ["accident", "construction", "roadblock", "breakdown"]
            incidents.append({
                "type": random.choice(incident_types),
                "severity": random.choice(["minor", "moderate", "major"]),
                "location_km": round(random.uniform(5, 100), 1),
                "expected_clearance_minutes": random.randint(15, 120)
            })
        return incidents
    
    async def get_road_closures(self, district_id: int) -> Dict:
        closures = []
        if random.random() > 0.8:
            closures.append({
                "road_name": f"Road_{random.randint(1, 50)}",
                "reason": random.choice(["maintenance", "construction", "flood", "landslide"]),
                "from_date": datetime.utcnow().isoformat(),
                "to_date": (datetime.utcnow() + timedelta(days=random.randint(1, 30))).isoformat(),
                "alternative_route_available": random.choice([True, False])
            })
        
        return {
            "district_id": district_id,
            "active_closures": closures,
            "total_closures": len(closures),
            "last_updated": datetime.utcnow().isoformat(),
            "data_source": "ROAD_INFRA_STUB"
        }
    
    async def get_flood_risk(self, district_id: int) -> Dict:
        risk_levels = ["none", "low", "moderate", "high", "severe"]
        
        affected_roads = []
        risk = random.choice(risk_levels)
        
        if risk in ["moderate", "high", "severe"]:
            for i in range(random.randint(1, 5)):
                affected_roads.append({
                    "road_id": f"R{random.randint(100, 999)}",
                    "road_name": f"Road_{i+1}",
                    "risk_level": random.choice(["low", "moderate", "high"]),
                    "water_level_cm": random.randint(5, 50)
                })
        
        return {
            "district_id": district_id,
            "overall_risk": risk,
            "affected_roads": affected_roads,
            "last_assessment": datetime.utcnow().isoformat(),
            "data_source": "ROAD_INFRA_STUB"
        }


road_infrastructure_stub = RoadInfrastructureStub()
