from typing import Dict, Any, List, Optional
import json

from ..base_agent import BaseAIAgent, AgentResponse
from ..prompts import PromptTemplates
from ....utils.logger import get_logger

logger = get_logger(__name__)


class RouteIntelligenceAgent(BaseAIAgent):
    def __init__(
        self,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.5,
        max_tokens: Optional[int] = 4096,
    ):
        super().__init__(
            agent_name="Route Intelligence Agent",
            system_prompt=PromptTemplates.SYSTEM_ROLE_ROUTE_INTELLIGENCE,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    async def analyze_route_async(
        self,
        origin: str,
        destinations: List[str],
        vehicle_type: str,
        total_capacity: float,
        current_load: float,
        priority_deliveries: Optional[List[str]] = None,
        max_driving_hours: float = 8.0,
        time_windows: str = "Standard business hours",
        road_conditions: str = "Normal",
    ) -> AgentResponse:
        prompt = PromptTemplates.format_route_optimization(
            origin=origin,
            destinations=destinations,
            vehicle_type=vehicle_type,
            total_capacity=total_capacity,
            current_load=current_load,
            priority_deliveries=priority_deliveries or [],
            max_driving_hours=max_driving_hours,
            time_windows=time_windows,
            road_conditions=road_conditions,
        )

        response_format = {"type": "json_object"}
        
        return await self.process_async(prompt, response_format=response_format)

    def analyze_route_sync(
        self,
        origin: str,
        destinations: List[str],
        vehicle_type: str,
        total_capacity: float,
        current_load: float,
        priority_deliveries: Optional[List[str]] = None,
        max_driving_hours: float = 8.0,
        time_windows: str = "Standard business hours",
        road_conditions: str = "Normal",
    ) -> AgentResponse:
        prompt = PromptTemplates.format_route_optimization(
            origin=origin,
            destinations=destinations,
            vehicle_type=vehicle_type,
            total_capacity=total_capacity,
            current_load=current_load,
            priority_deliveries=priority_deliveries or [],
            max_driving_hours=max_driving_hours,
            time_windows=time_windows,
            road_conditions=road_conditions,
        )

        response_format = {"type": "json_object"}
        
        return self.process_sync(prompt, response_format=response_format)

    async def estimate_delivery_async(
        self,
        origin: str,
        destination: str,
        weight: float,
        dimensions: str,
        priority: str,
        distance: float,
        stops: int,
        road_type: str = "Mixed",
    ) -> AgentResponse:
        prompt = PromptTemplates.format_delivery_estimation(
            origin=origin,
            destination=destination,
            weight=weight,
            dimensions=dimensions,
            priority=priority,
            distance=distance,
            stops=stops,
            road_type=road_type,
        )

        response_format = {"type": "json_object"}
        
        return await self.process_async(prompt, response_format=response_format)

    def estimate_delivery_sync(
        self,
        origin: str,
        destination: str,
        weight: float,
        dimensions: str,
        priority: str,
        distance: float,
        stops: int,
        road_type: str = "Mixed",
    ) -> AgentResponse:
        prompt = PromptTemplates.format_delivery_estimation(
            origin=origin,
            destination=destination,
            weight=weight,
            dimensions=dimensions,
            priority=priority,
            distance=distance,
            stops=stops,
            road_type=road_type,
        )

        response_format = {"type": "json_object"}
        
        return self.process_sync(prompt, response_format=response_format)

    async def analyze(
        self,
        route_data: Dict[str, Any],
        **kwargs
    ) -> AgentResponse:
        return await self.analyze_route_async(
            origin=route_data.get("origin", ""),
            destinations=route_data.get("destinations", []),
            vehicle_type=route_data.get("vehicle_type", "Standard"),
            total_capacity=route_data.get("total_capacity", 0),
            current_load=route_data.get("current_load", 0),
            priority_deliveries=route_data.get("priority_deliveries", []),
            max_driving_hours=route_data.get("max_driving_hours", 8.0),
            time_windows=route_data.get("time_windows", "Standard business hours"),
            road_conditions=route_data.get("road_conditions", "Normal"),
        )

    async def get_recommendations(
        self,
        context: str,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        prompt = f"""Based on the following context, provide route optimization recommendations:

Context:
{context}

Constraints:
{json.dumps(constraints or {}, indent=2)}

Please provide your recommendations in JSON format with the following structure:
{{
    "primary_recommendation": "Description of the main recommendation",
    "estimated_improvements": {{
        "time_savings": "estimated time savings",
        "cost_savings": "estimated cost savings",
        "efficiency_gain": "percentage improvement"
    }},
    "alternative_options": [
        {{
            "description": "alternative approach",
            "pros": ["list of advantages"],
            "cons": ["list of disadvantages"]
        }}
    ],
    "implementation_steps": ["step 1", "step 2", ...],
    "risk_factors": ["risk 1", "risk 2", ...]
}}"""

        response_format = {"type": "json_object"}
        return await self.process_async(prompt, response_format=response_format)

    async def compare_routes_async(
        self,
        routes: List[Dict[str, Any]],
        criteria: Optional[List[str]] = None,
    ) -> AgentResponse:
        criteria = criteria or ["time", "cost", "distance", "fuel_efficiency"]
        
        prompt = f"""Compare the following delivery routes and recommend the best option:

Routes:
{json.dumps(routes, indent=2)}

Comparison Criteria: {', '.join(criteria)}

Please provide your analysis in JSON format with the following structure:
{{
    "recommended_route": "route identifier or index",
    "comparison_matrix": {{
        "route_1": {{
            "time_score": 0-10,
            "cost_score": 0-10,
            "distance_score": 0-10,
            "fuel_efficiency_score": 0-10,
            "overall_score": 0-10
        }},
        ...
    }},
    "analysis": "Detailed explanation of the comparison",
    "trade_offs": "Description of key trade-offs between routes"
}}"""

        response_format = {"type": "json_object"}
        return await self.process_async(prompt, response_format=response_format)
