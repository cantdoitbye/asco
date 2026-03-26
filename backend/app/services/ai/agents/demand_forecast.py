from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from ..base_agent import BaseAIAgent, AgentResponse
from ..prompts import PromptTemplates
from ....utils.logger import get_logger

logger = get_logger(__name__)


class DemandForecastingAgent(BaseAIAgent):
    def __init__(
        self,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.4,
        max_tokens: Optional[int] = 4096,
    ):
        super().__init__(
            agent_name="Demand Forecasting Agent",
            system_prompt=PromptTemplates.SYSTEM_ROLE_DEMAND_FORECAST,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        self._forecast_config = {
            "default_historical_days": 90,
            "default_forecast_days": 30,
            "confidence_threshold": 0.7,
        }

    async def generate_forecast(
        self,
        historical_data: List[Dict[str, Any]],
        forecast_days: int = 7,
        include_seasonality: bool = True
    ) -> Dict[str, Any]:
        total_beneficiaries = sum(d.get("total_beneficiaries", 0) for d in historical_data) or 100
        children_0_3 = sum(d.get("children_0_3", 0) for d in historical_data) or 30
        children_3_6 = sum(d.get("children_3_6", 0) for d in historical_data) or 40
        pregnant_women = sum(d.get("pregnant_women", 0) for d in historical_data) or 15
        lactating_mothers = sum(d.get("lactating_mothers", 0) for d in historical_data) or 15
        
        num_centers = len(historical_data) if historical_data else 1
        
        base_demand_per_beneficiary = 0.5
        daily_demand = total_beneficiaries * base_demand_per_beneficiary
        
        seasonal_multiplier = 1.0
        if include_seasonality:
            from datetime import datetime
            month = datetime.now().month
            if month in [6, 7, 8, 9]:
                seasonal_multiplier = 1.15
            elif month in [12, 1, 2]:
                seasonal_multiplier = 0.95
        
        adjusted_daily_demand = daily_demand * seasonal_multiplier
        total_forecast_demand = adjusted_daily_demand * forecast_days
        
        confidence = 0.82 if num_centers >= 5 else 0.65
        
        forecasts = [
            {
                "item_id": 1,
                "item_name": "Rice",
                "current_demand": round(total_forecast_demand * 0.4),
                "predicted_demand": round(total_forecast_demand * 0.45),
                "confidence": round(confidence * 100, 1),
                "trend": "up",
                "period": f"{forecast_days}_days"
            },
            {
                "item_id": 2,
                "item_name": "Wheat",
                "current_demand": round(total_forecast_demand * 0.25),
                "predicted_demand": round(total_forecast_demand * 0.28),
                "confidence": round(confidence * 100 - 5, 1),
                "trend": "up",
                "period": f"{forecast_days}_days"
            },
            {
                "item_id": 3,
                "item_name": "Pulses",
                "current_demand": round(total_forecast_demand * 0.15),
                "predicted_demand": round(total_forecast_demand * 0.16),
                "confidence": round(confidence * 100, 1),
                "trend": "stable",
                "period": f"{forecast_days}_days"
            },
            {
                "item_id": 4,
                "item_name": "Oil",
                "current_demand": round(total_forecast_demand * 0.1),
                "predicted_demand": round(total_forecast_demand * 0.11),
                "confidence": round(confidence * 100 - 3, 1),
                "trend": "up",
                "period": f"{forecast_days}_days"
            },
            {
                "item_id": 5,
                "item_name": "Sugar",
                "current_demand": round(total_forecast_demand * 0.08),
                "predicted_demand": round(total_forecast_demand * 0.08),
                "confidence": round(confidence * 100, 1),
                "trend": "stable",
                "period": f"{forecast_days}_days"
            }
        ]
        
        return {
            "forecasts": forecasts,
            "confidence_level": round(confidence * 100, 1),
            "seasonal_adjustment": seasonal_multiplier,
            "recommendations": [
                "Consider increasing rice stock by 12% for the forecast period",
                "Monitor pulse consumption patterns for optimization",
                f"Total beneficiary count: {total_beneficiaries} across {num_centers} centers"
            ]
        }

    async def generate_forecast_async(
        self,
        historical_data: str,
        current_inventory: str,
        scheduled_distributions: str,
        seasonal_factors: str,
        special_events: str,
        center_count: int,
        historical_days: int = 90,
        forecast_days: int = 30,
    ) -> AgentResponse:
        prompt = PromptTemplates.format_demand_forecast(
            historical_data=historical_data,
            current_inventory=current_inventory,
            scheduled_distributions=scheduled_distributions,
            seasonal_factors=seasonal_factors,
            special_events=special_events,
            center_count=center_count,
            historical_days=historical_days,
            forecast_days=forecast_days,
        )

        response_format = {"type": "json_object"}
        
        return await self.process_async(prompt, response_format=response_format)

    def generate_forecast_sync(
        self,
        historical_data: str,
        current_inventory: str,
        scheduled_distributions: str,
        seasonal_factors: str,
        special_events: str,
        center_count: int,
        historical_days: int = 90,
        forecast_days: int = 30,
    ) -> AgentResponse:
        prompt = PromptTemplates.format_demand_forecast(
            historical_data=historical_data,
            current_inventory=current_inventory,
            scheduled_distributions=scheduled_distributions,
            seasonal_factors=seasonal_factors,
            special_events=special_events,
            center_count=center_count,
            historical_days=historical_days,
            forecast_days=forecast_days,
        )

        response_format = {"type": "json_object"}
        
        return self.process_sync(prompt, response_format=response_format)

    async def get_inventory_recommendations_async(
        self,
        current_stock: str,
        demand_patterns: str,
        lead_times: str,
        max_capacity: str,
        temperature_req: str = "Ambient",
        shelf_life: str = "Standard",
    ) -> AgentResponse:
        prompt = PromptTemplates.format_inventory_recommendation(
            current_stock=current_stock,
            demand_patterns=demand_patterns,
            lead_times=lead_times,
            max_capacity=max_capacity,
            temperature_req=temperature_req,
            shelf_life=shelf_life,
        )

        response_format = {"type": "json_object"}
        
        return await self.process_async(prompt, response_format=response_format)

    def get_inventory_recommendations_sync(
        self,
        current_stock: str,
        demand_patterns: str,
        lead_times: str,
        max_capacity: str,
        temperature_req: str = "Ambient",
        shelf_life: str = "Standard",
    ) -> AgentResponse:
        prompt = PromptTemplates.format_inventory_recommendation(
            current_stock=current_stock,
            demand_patterns=demand_patterns,
            lead_times=lead_times,
            max_capacity=max_capacity,
            temperature_req=temperature_req,
            shelf_life=shelf_life,
        )

        response_format = {"type": "json_object"}
        
        return self.process_sync(prompt, response_format=response_format)

    async def analyze(
        self,
        forecast_data: Dict[str, Any],
        **kwargs
    ) -> AgentResponse:
        return await self.generate_forecast_async(
            historical_data=forecast_data.get("historical_data", ""),
            current_inventory=forecast_data.get("current_inventory", ""),
            scheduled_distributions=forecast_data.get("scheduled_distributions", ""),
            seasonal_factors=forecast_data.get("seasonal_factors", ""),
            special_events=forecast_data.get("special_events", ""),
            center_count=forecast_data.get("center_count", 0),
            historical_days=forecast_data.get("historical_days", 90),
            forecast_days=forecast_data.get("forecast_days", 30),
        )

    async def get_recommendations(
        self,
        context: str,
        forecast_horizon: int = 30,
    ) -> AgentResponse:
        prompt = f"""Based on the following context, provide demand forecasting recommendations:

Context:
{context}

Forecast Horizon: {forecast_horizon} days

Please provide your recommendations in JSON format with the following structure:
{{
    "demand_outlook": {{
        "trend": "increasing/stable/decreasing",
        "volatility": "high/medium/low",
        "seasonality_impact": "description of seasonal effects"
    }},
    "inventory_recommendations": [
        {{
            "item": "item name",
            "current_stock": "current level",
            "recommended_stock": "recommended level",
            "action": "reorder/maintain/reduce",
            "priority": "high/medium/low"
        }}
    ],
    "procurement_timing": {{
        "optimal_order_date": "recommended date",
        "quantity": "recommended quantity",
        "reasoning": "explanation"
    }},
    "risk_factors": [
        {{
            "factor": "description",
            "probability": "high/medium/low",
            "impact": "high/medium/low",
            "mitigation": "suggested action"
        }}
    ],
    "key_metrics_to_monitor": [
        "metric 1",
        "metric 2"
    ],
    "confidence_level": 0-100
}}"""

        response_format = {"type": "json_object"}
        return await self.process_async(prompt, response_format=response_format)

    async def analyze_seasonal_patterns_async(
        self,
        historical_data: List[Dict[str, Any]],
        item_category: Optional[str] = None,
    ) -> AgentResponse:
        prompt = f"""Analyze seasonal patterns in the following historical demand data:

Historical Data:
{json.dumps(historical_data, indent=2)}

Item Category: {item_category or "All categories"}

Please provide your analysis in JSON format with the following structure:
{{
    "seasonal_patterns": [
        {{
            "season": "spring/summer/monsoon/autumn/winter",
            "demand_multiplier": 1.0,
            "peak_items": ["item 1", "item 2"],
            "low_demand_items": ["item 1", "item 2"],
            "special_considerations": "notes"
        }}
    ],
    "yearly_trends": {{
        "overall_growth_rate": "percentage",
        "trend_direction": "increasing/stable/decreasing",
        "notable_changes": ["change 1", "change 2"]
    }},
    "cyclic_patterns": [
        {{
            "pattern": "description",
            "frequency": "weekly/monthly/quarterly",
            "amplitude": "high/medium/low"
        }}
    ],
    "anomalous_periods": [
        {{
            "period": "date range",
            "anomaly_type": "spike/drop",
            "possible_causes": ["cause 1", "cause 2"]
        }}
    ],
    "forecast_adjustments": "recommended adjustments for forecasting"
}}"""

        response_format = {"type": "json_object"}
        return await self.process_async(prompt, response_format=response_format)

    async def compare_forecast_methods_async(
        self,
        data: Dict[str, Any],
        methods: Optional[List[str]] = None,
    ) -> AgentResponse:
        methods = methods or ["moving_average", "exponential_smoothing", "seasonal_decomposition"]
        
        prompt = f"""Compare different forecasting methods for the following data:

Data:
{json.dumps(data, indent=2)}

Methods to Compare: {', '.join(methods)}

Please provide your comparison in JSON format with the following structure:
{{
    "recommended_method": "method name",
    "method_comparison": [
        {{
            "method": "method name",
            "accuracy_score": 0-100,
            "strengths": ["strength 1", "strength 2"],
            "weaknesses": ["weakness 1", "weakness 2"],
            "best_use_case": "when to use this method"
        }}
    ],
    "ensemble_recommendation": {{
        "use_ensemble": true/false,
        "weighted_methods": [
            {{
                "method": "method name",
                "weight": 0.0-1.0
            }}
        ],
        "expected_improvement": "description"
    }},
    "data_characteristics": {{
        "trend": "present/absent",
        "seasonality": "strong/moderate/weak",
        "noise_level": "high/medium/low",
        "stationarity": "stationary/non-stationary"
    }}
}}"""

        response_format = {"type": "json_object"}
        return await self.process_async(prompt, response_format=response_format)

    async def generate_scenario_analysis_async(
        self,
        base_forecast: Dict[str, Any],
        scenarios: List[Dict[str, str]],
    ) -> AgentResponse:
        prompt = f"""Perform scenario analysis on the following base forecast:

Base Forecast:
{json.dumps(base_forecast, indent=2)}

Scenarios to Analyze:
{json.dumps(scenarios, indent=2)}

Please provide your scenario analysis in JSON format with the following structure:
{{
    "scenarios": [
        {{
            "scenario_name": "name",
            "description": "what this scenario represents",
            "demand_impact": {{
                "change_percentage": -20 to +20,
                "affected_items": ["item 1", "item 2"],
                "timeline": "immediate/short-term/long-term"
            }},
            "adjusted_forecast": {{
                "total_demand": "adjusted value",
                "peak_periods": ["period 1", "period 2"],
                "critical_items": ["item 1", "item 2"]
            }},
            "probability": "high/medium/low",
            "preparation_recommendations": ["rec 1", "rec 2"]
        }}
    ],
    "best_case_outlook": "description",
    "worst_case_outlook": "description",
    "most_likely_outlook": "description",
    "contingency_plans": [
        {{
            "trigger": "what triggers this plan",
            "actions": ["action 1", "action 2"]
        }}
    ]
}}"""

        response_format = {"type": "json_object"}
        return await self.process_async(prompt, response_format=response_format)

    def set_forecast_config(
        self,
        default_historical_days: Optional[int] = None,
        default_forecast_days: Optional[int] = None,
        confidence_threshold: Optional[float] = None,
    ):
        if default_historical_days is not None:
            self._forecast_config["default_historical_days"] = default_historical_days
        if default_forecast_days is not None:
            self._forecast_config["default_forecast_days"] = default_forecast_days
        if confidence_threshold is not None:
            self._forecast_config["confidence_threshold"] = confidence_threshold

    def get_forecast_config(self) -> Dict[str, Any]:
        return self._forecast_config.copy()
