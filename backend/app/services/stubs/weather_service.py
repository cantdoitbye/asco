from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random


class WeatherServiceStub:
    def __init__(self):
        self.base_url = "https://imd.gov.in/api/weather/v1"
    
    async def get_current_weather(self, latitude: float, longitude: float) -> Dict:
        conditions = ["sunny", "cloudy", "rainy", "stormy", "foggy", "windy"]
        condition = random.choice(conditions)
        
        return {
            "location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "current": {
                "condition": condition,
                "temperature_celsius": round(random.uniform(20, 40), 1),
                "humidity_percent": random.randint(30, 90),
                "wind_speed_kmh": round(random.uniform(5, 30), 1),
                "wind_direction": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
                "visibility_km": round(random.uniform(2, 15), 1),
                "pressure_hpa": round(random.uniform(990, 1020), 1)
            },
            "timestamp": datetime.utcnow().isoformat(),
            "data_source": "IMD_STUB"
        }
    
    async def get_forecast(self, latitude: float, longitude: float, days: int = 5) -> Dict:
        conditions = ["sunny", "cloudy", "rainy", "stormy", "partly_cloudy"]
        forecast = []
        
        for i in range(days):
            date = datetime.utcnow() + timedelta(days=i)
            forecast.append({
                "date": date.strftime("%Y-%m-%d"),
                "condition": random.choice(conditions),
                "temp_high": round(random.uniform(28, 38), 1),
                "temp_low": round(random.uniform(18, 26), 1),
                "precipitation_chance": random.randint(0, 100),
                "humidity_percent": random.randint(30, 85),
                "wind_speed_kmh": round(random.uniform(5, 25), 1)
            })
        
        return {
            "location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "forecast": forecast,
            "generated_at": datetime.utcnow().isoformat(),
            "data_source": "IMD_STUB"
        }
    
    async def get_weather_alerts(self, district_id: int) -> Dict:
        alert_types = ["heavy_rain", "heat_wave", "cold_wave", "thunderstorm", "fog", "cyclone"]
        has_alert = random.choice([True, False])
        
        alerts = []
        if has_alert:
            alerts.append({
                "type": random.choice(alert_types),
                "severity": random.choice(["low", "moderate", "high", "severe"]),
                "description": "Weather alert for the region",
                "valid_from": datetime.utcnow().isoformat(),
                "valid_until": (datetime.utcnow() + timedelta(hours=random.randint(12, 48))).isoformat(),
                "district_id": district_id
            })
        
        return {
            "district_id": district_id,
            "alerts": alerts,
            "has_active_alerts": len(alerts) > 0,
            "last_updated": datetime.utcnow().isoformat(),
            "data_source": "IMD_STUB"
        }
    
    async def get_rainfall_data(self, district_id: int, days: int = 30) -> Dict:
        daily_rainfall = []
        total_rainfall = 0
        
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=i)
            rainfall = round(random.uniform(0, 50), 1) if random.random() > 0.3 else 0
            total_rainfall += rainfall
            daily_rainfall.append({
                "date": date.strftime("%Y-%m-%d"),
                "rainfall_mm": rainfall
            })
        
        return {
            "district_id": district_id,
            "period_days": days,
            "total_rainfall_mm": round(total_rainfall, 1),
            "average_daily_mm": round(total_rainfall / days, 1),
            "daily_data": daily_rainfall,
            "data_source": "IMD_STUB"
        }


weather_service_stub = WeatherServiceStub()
