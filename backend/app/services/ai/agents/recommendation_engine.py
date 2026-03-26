from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import json

from ..base_agent import BaseAIAgent, AgentResponse
from ..openai_client import OpenAIClient
from ....utils.logger import get_logger

logger = get_logger(__name__)


class RecommendationPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecommendationCategory(str, Enum):
    SUPPLY_OPTIMIZATION = "supply_optimization"
    ROUTE_IMPROVEMENT = "route_improvement"
    INVENTORY_MANAGEMENT = "inventory_management"
    STAKEHOLDER_ENGAGEMENT = "stakeholder_engagement"
    COMPLIANCE = "compliance"
    DEMAND_FORECAST = "demand_forecast"
    COST_REDUCTION = "cost_reduction"
    QUALITY_IMPROVEMENT = "quality_improvement"


RECOMMENDATION_SYSTEM_PROMPT = """You are the Recommendation Engine for the Ooumph SHAKTI supply chain management system.
Your role is to analyze data and provide actionable recommendations to improve supply chain efficiency, reduce costs, and enhance service delivery.

You have expertise in:
- Supply chain optimization
- Route planning and logistics
- Inventory management
- Demand forecasting
- Stakeholder management
- Cost-benefit analysis
- Government program compliance

Always provide specific, actionable recommendations with clear rationale and expected impact."""


class RecommendationEngine(BaseAIAgent):
    def __init__(self):
        super().__init__(
            agent_name="RecommendationEngine",
            system_prompt=RECOMMENDATION_SYSTEM_PROMPT,
            model="gpt-4-turbo-preview",
            temperature=0.4,
        )
        self.recommendations_store: List[Dict[str, Any]] = []

    async def generate_recommendations(
        self,
        context: Dict[str, Any],
        user_role: str,
        district_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        prompt = f"""
Generate personalized recommendations based on the following context:

User Role: {user_role}
District ID: {district_id or 'All districts'}

Context Data:
{json.dumps(context, indent=2)}

Please provide 5-10 specific, actionable recommendations in JSON format as an array, where each recommendation contains:
1. id: Unique identifier (uuid format)
2. title: Short title for the recommendation
3. description: Detailed description of the recommendation
4. category: One of {json.dumps([c.value for c in RecommendationCategory])}
5. priority: One of {json.dumps([p.value for p in RecommendationPriority])}
6. impact: Expected impact (high, medium, low)
7. effort: Implementation effort (high, medium, low)
8. timeframe: Suggested implementation timeframe
9. actions: List of specific actions to implement
10. metrics: List of metrics to track success
11. stakeholders: List of stakeholders involved
12. confidence: Confidence level (0-1)
"""

        response = await self.process_async(
            user_input=prompt,
            response_format={"type": "json_object"}
        )

        if response.success:
            recommendations = response.content.get("recommendations", [])
            for rec in recommendations:
                rec["created_at"] = datetime.utcnow().isoformat()
                rec["status"] = "pending"
                self.recommendations_store.append(rec)
            return recommendations
        else:
            logger.error(f"Recommendation generation failed: {response.error}")
            return self._get_fallback_recommendations(user_role)

    def _get_fallback_recommendations(self, user_role: str) -> List[Dict[str, Any]]:
        return [
            {
                "id": "rec-001",
                "title": "Optimize Delivery Routes",
                "description": "Review and optimize delivery routes to reduce travel time and fuel costs",
                "category": RecommendationCategory.ROUTE_IMPROVEMENT.value,
                "priority": RecommendationPriority.HIGH.value,
                "impact": "high",
                "effort": "medium",
                "timeframe": "2-4 weeks",
                "actions": ["Analyze current routes", "Identify inefficiencies", "Implement optimizations"],
                "metrics": ["Delivery time", "Fuel consumption", "Cost per delivery"],
                "stakeholders": ["Transport Team", "Suppliers"],
                "confidence": 0.85,
                "created_at": datetime.utcnow().isoformat(),
                "status": "pending"
            },
            {
                "id": "rec-002",
                "title": "Review Inventory Levels",
                "description": "Analyze inventory levels to prevent stockouts and reduce waste",
                "category": RecommendationCategory.INVENTORY_MANAGEMENT.value,
                "priority": RecommendationPriority.MEDIUM.value,
                "impact": "medium",
                "effort": "low",
                "timeframe": "1-2 weeks",
                "actions": ["Review current stock", "Adjust reorder points", "Update forecasts"],
                "metrics": ["Stockout rate", "Waste percentage", "Inventory turnover"],
                "stakeholders": ["Warehouse Team", "Suppliers"],
                "confidence": 0.80,
                "created_at": datetime.utcnow().isoformat(),
                "status": "pending"
            }
        ]

    async def get_contextual_recommendations(
        self,
        user_id: int,
        user_role: str,
        current_page: str
    ) -> List[Dict[str, Any]]:
        page_context = {
            "dashboard": ["supply_optimization", "demand_forecast"],
            "deliveries": ["route_improvement", "cost_reduction"],
            "inventory": ["inventory_management", "quality_improvement"],
            "grievances": ["stakeholder_engagement", "quality_improvement"],
            "trust-scores": ["stakeholder_engagement", "compliance"]
        }
        
        relevant_categories = page_context.get(current_page, [])
        
        filtered = [
            rec for rec in self.recommendations_store
            if rec.get("category") in relevant_categories or not relevant_categories
        ]
        
        return filtered[:5]

    def calculate_priority_score(
        self,
        recommendation: Dict[str, Any]
    ) -> float:
        priority_weights = {
            RecommendationPriority.CRITICAL.value: 1.0,
            RecommendationPriority.HIGH.value: 0.8,
            RecommendationPriority.MEDIUM.value: 0.6,
            RecommendationPriority.LOW.value: 0.4
        }
        
        impact_weights = {"high": 1.0, "medium": 0.7, "low": 0.4}
        effort_weights = {"low": 1.0, "medium": 0.7, "high": 0.4}
        
        priority = priority_weights.get(recommendation.get("priority", "medium"), 0.6)
        impact = impact_weights.get(recommendation.get("impact", "medium"), 0.7)
        effort = effort_weights.get(recommendation.get("effort", "medium"), 0.7)
        confidence = recommendation.get("confidence", 0.5)
        
        return (priority * 0.3 + impact * 0.3 + effort * 0.2 + confidence * 0.2) * 100

    async def filter_by_role(
        self,
        recommendations: List[Dict[str, Any]],
        user_role: str
    ) -> List[Dict[str, Any]]:
        role_categories = {
            "admin": list(RecommendationCategory),
            "cdpo": [
                RecommendationCategory.SUPPLY_OPTIMIZATION,
                RecommendationCategory.STAKEHOLDER_ENGAGEMENT,
                RecommendationCategory.COMPLIANCE
            ],
            "supervisor": [
                RecommendationCategory.ROUTE_IMPROVEMENT,
                RecommendationCategory.QUALITY_IMPROVEMENT
            ],
            "anganwadi_worker": [
                RecommendationCategory.INVENTORY_MANAGEMENT,
                RecommendationCategory.DEMAND_FORECAST
            ],
            "supplier": [
                RecommendationCategory.COST_REDUCTION,
                RecommendationCategory.QUALITY_IMPROVEMENT
            ]
        }
        
        allowed_categories = role_categories.get(user_role, [])
        allowed_values = [c.value for c in allowed_categories]
        
        return [
            rec for rec in recommendations
            if rec.get("category") in allowed_values
        ]

    def get_all_recommendations(self) -> List[Dict[str, Any]]:
        return self.recommendations_store

    def update_recommendation_status(
        self,
        recommendation_id: str,
        status: str
    ) -> Optional[Dict[str, Any]]:
        for rec in self.recommendations_store:
            if rec.get("id") == recommendation_id:
                rec["status"] = status
                rec["updated_at"] = datetime.utcnow().isoformat()
                return rec
        return None

    async def analyze(self, data: Dict[str, Any]) -> AgentResponse:
        recommendations = await self.generate_recommendations(
            context=data.get("context", {}),
            user_role=data.get("user_role", "admin"),
            district_id=data.get("district_id")
        )
        return AgentResponse(
            success=True,
            content=recommendations,
            agent_name=self.agent_name
        )

    async def get_recommendations(self, data: Dict[str, Any]) -> AgentResponse:
        contextual = await self.get_contextual_recommendations(
            user_id=data.get("user_id", 0),
            user_role=data.get("user_role", "admin"),
            current_page=data.get("current_page", "dashboard")
        )
        return AgentResponse(
            success=True,
            content=contextual,
            agent_name=self.agent_name
        )


recommendation_engine = RecommendationEngine()
