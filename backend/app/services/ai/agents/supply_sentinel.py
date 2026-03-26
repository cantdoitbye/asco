from typing import Dict, Any, List, Optional
from enum import Enum
import json

from ..base_agent import BaseAIAgent, AgentResponse
from ..prompts import PromptTemplates
from ....utils.logger import get_logger

logger = get_logger(__name__)


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SupplySentinelAgent(BaseAIAgent):
    def __init__(
        self,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.3,
        max_tokens: Optional[int] = 4096,
    ):
        super().__init__(
            agent_name="Supply Sentinel Agent",
            system_prompt=PromptTemplates.SYSTEM_ROLE_SUPPLY_SENTINEL,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        self._alert_thresholds = {
            "stockout_days": 7,
            "low_stock_percentage": 20,
            "critical_stock_percentage": 10,
        }

    async def monitor_inventory_async(
        self,
        inventory_status: str,
        consumption_patterns: str,
        supplier_info: str,
        weather_conditions: str = "Normal",
        regional_events: str = "None",
        transportation_status: str = "Operational",
    ) -> AgentResponse:
        prompt = PromptTemplates.format_supply_alert(
            inventory_status=inventory_status,
            consumption_patterns=consumption_patterns,
            supplier_info=supplier_info,
            weather_conditions=weather_conditions,
            regional_events=regional_events,
            transportation_status=transportation_status,
        )

        response_format = {"type": "json_object"}
        
        return await self.process_async(prompt, response_format=response_format)

    def monitor_inventory_sync(
        self,
        inventory_status: str,
        consumption_patterns: str,
        supplier_info: str,
        weather_conditions: str = "Normal",
        regional_events: str = "None",
        transportation_status: str = "Operational",
    ) -> AgentResponse:
        prompt = PromptTemplates.format_supply_alert(
            inventory_status=inventory_status,
            consumption_patterns=consumption_patterns,
            supplier_info=supplier_info,
            weather_conditions=weather_conditions,
            regional_events=regional_events,
            transportation_status=transportation_status,
        )

        response_format = {"type": "json_object"}
        
        return self.process_sync(prompt, response_format=response_format)

    async def detect_anomaly_async(
        self,
        data_context: str,
        current_readings: str,
        historical_baseline: str,
        expected_min: float,
        expected_max: float,
    ) -> AgentResponse:
        prompt = PromptTemplates.format_anomaly_detection(
            data_context=data_context,
            current_readings=current_readings,
            historical_baseline=historical_baseline,
            expected_min=expected_min,
            expected_max=expected_max,
        )

        response_format = {"type": "json_object"}
        
        return await self.process_async(prompt, response_format=response_format)

    def detect_anomaly_sync(
        self,
        data_context: str,
        current_readings: str,
        historical_baseline: str,
        expected_min: float,
        expected_max: float,
    ) -> AgentResponse:
        prompt = PromptTemplates.format_anomaly_detection(
            data_context=data_context,
            current_readings=current_readings,
            historical_baseline=historical_baseline,
            expected_min=expected_min,
            expected_max=expected_max,
        )

        response_format = {"type": "json_object"}
        
        return self.process_sync(prompt, response_format=response_format)

    async def analyze(
        self,
        supply_data: Dict[str, Any],
        **kwargs
    ) -> AgentResponse:
        return await self.monitor_inventory_async(
            inventory_status=supply_data.get("inventory_status", ""),
            consumption_patterns=supply_data.get("consumption_patterns", ""),
            supplier_info=supply_data.get("supplier_info", ""),
            weather_conditions=supply_data.get("weather_conditions", "Normal"),
            regional_events=supply_data.get("regional_events", "None"),
            transportation_status=supply_data.get("transportation_status", "Operational"),
        )

    async def get_recommendations(
        self,
        context: str,
        risk_level: str = "medium",
    ) -> AgentResponse:
        prompt = f"""Based on the following supply chain context, provide risk mitigation recommendations:

Context:
{context}

Current Risk Level: {risk_level}

Please provide your recommendations in JSON format with the following structure:
{{
    "immediate_actions": [
        {{
            "action": "description of action",
            "priority": "high/medium/low",
            "estimated_impact": "description of expected impact",
            "responsible_party": "suggested owner"
        }}
    ],
    "preventive_measures": [
        {{
            "measure": "description",
            "implementation_timeline": "estimated time to implement",
            "resource_requirements": "what's needed"
        }}
    ],
    "monitoring_suggestions": [
        "metric or indicator to monitor"
    ],
    "escalation_triggers": [
        {{
            "condition": "what to watch for",
            "action": "what to do if triggered"
        }}
    ],
    "risk_mitigation_score": 0-100
}}"""

        response_format = {"type": "json_object"}
        return await self.process_async(prompt, response_format=response_format)

    async def assess_supplier_risk_async(
        self,
        supplier_data: List[Dict[str, Any]],
    ) -> AgentResponse:
        prompt = f"""Assess the risk level of the following suppliers:

Suppliers:
{json.dumps(supplier_data, indent=2)}

Please provide your assessment in JSON format with the following structure:
{{
    "overall_supply_chain_risk": "low/medium/high/critical",
    "supplier_assessments": [
        {{
            "supplier_id": "id",
            "supplier_name": "name",
            "risk_level": "low/medium/high/critical",
            "risk_factors": ["factor 1", "factor 2"],
            "reliability_score": 0-100,
            "recommended_actions": ["action 1", "action 2"]
        }}
    ],
    "critical_dependencies": ["supplier or item that poses highest risk"],
    "diversification_recommendations": ["recommendation 1", "recommendation 2"],
    "summary": "Overall assessment summary"
}}"""

        response_format = {"type": "json_object"}
        return await self.process_async(prompt, response_format=response_format)

    async def generate_alert_async(
        self,
        alert_type: str,
        severity: str,
        details: Dict[str, Any],
        affected_items: List[str],
    ) -> AgentResponse:
        prompt = f"""Generate a supply chain alert with the following parameters:

Alert Type: {alert_type}
Severity: {severity}
Details: {json.dumps(details, indent=2)}
Affected Items: {', '.join(affected_items)}

Please generate an alert in JSON format with the following structure:
{{
    "alert_id": "unique identifier",
    "title": "Alert title",
    "description": "Detailed alert description",
    "severity": "{severity}",
    "category": "stockout/delay/quality/supplier/other",
    "affected_items": {json.dumps(affected_items)},
    "recommended_actions": [
        {{
            "action": "description",
            "priority": "high/medium/low",
            "deadline": "suggested deadline"
        }}
    ],
    "escalation_required": true/false,
    "notification_recipients": ["role or department to notify"],
    "created_at": "ISO timestamp"
}}"""

        response_format = {"type": "json_object"}
        return await self.process_async(prompt, response_format=response_format)

    def set_alert_thresholds(
        self,
        stockout_days: Optional[int] = None,
        low_stock_percentage: Optional[float] = None,
        critical_stock_percentage: Optional[float] = None,
    ):
        if stockout_days is not None:
            self._alert_thresholds["stockout_days"] = stockout_days
        if low_stock_percentage is not None:
            self._alert_thresholds["low_stock_percentage"] = low_stock_percentage
        if critical_stock_percentage is not None:
            self._alert_thresholds["critical_stock_percentage"] = critical_stock_percentage

    def get_alert_thresholds(self) -> Dict[str, Any]:
        return self._alert_thresholds.copy()
