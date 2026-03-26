from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from ..base_agent import BaseAIAgent, AgentResponse
from ..openai_client import OpenAIClient
from ....utils.logger import get_logger

logger = get_logger(__name__)


GRIEVANCE_SYSTEM_PROMPT = """You are the Grievance Intelligence Agent (GIA) for the Ooumph SHAKTI supply chain management system.
Your role is to analyze grievances, detect patterns, assess sentiment, and provide intelligent recommendations.

You have expertise in:
- Natural Language Processing for complaint analysis
- Sentiment analysis across multiple languages (Telugu, Hindi, English)
- Pattern detection for recurring issues
- Risk assessment and flagging
- Auto-categorization of grievances
- Supply chain issue identification

Always provide accurate, unbiased analysis with clear reasoning."""


class GrievanceIntelligenceAgent(BaseAIAgent):
    def __init__(self):
        super().__init__(
            agent_name="GrievanceIntelligenceAgent",
            system_prompt=GRIEVANCE_SYSTEM_PROMPT,
            model="gpt-4-turbo-preview",
            temperature=0.3,
        )

    def analyze(self, grievance_text: str) -> AgentResponse:
        return self.process_sync(
            user_input=f"Analyze this grievance: {grievance_text}",
            response_format={"type": "json_object"}
        )

    def get_recommendations(self, grievance_data: Dict[str, Any]) -> AgentResponse:
        return self.process_sync(
            user_input=f"Provide recommendations for: {json.dumps(grievance_data)}",
            response_format={"type": "json_object"}
        )

    async def analyze_grievance(
        self,
        grievance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        grievance_text = grievance_data.get("complaint", "")
        if not grievance_text:
            return {"error": "Complaint text is required"}

        prompt = f"""
Analyze the following grievance and provide comprehensive analysis.

Grievance Details:
- ID: {grievance_data.get('id', 'N/A')}
- Complainant: {grievance_data.get('complainant_name', 'Anonymous')}
- Type: {grievance_data.get('type', 'General')}
- Date: {grievance_data.get('created_at', datetime.utcnow().isoformat())}

Complaint Text:
{grievance_text}

Please provide analysis in JSON format with:
1. category: Primary category (supply, delivery, quality, staff, infrastructure, other)
2. subcategory: Specific subcategory
3. sentiment: Overall sentiment (positive, negative, neutral)
4. sentiment_score: Sentiment score from -1 to 1
5. urgency: Urgency level (high, medium, low)
6. risk_level: Risk assessment (critical, high, medium, low)
7. risk_factors: List of identified risk factors
8. key_issues: List of key issues extracted
9. affected_beneficiaries: Estimated number affected
10. recommended_actions: List of recommended actions
11. language_detected: Detected language (english, hindi, telugu)
12. confidence_score: Confidence in analysis (0-1)
13. summary: Brief summary of the grievance
"""

        response = await self.process_async(
            user_input=prompt,
            response_format={"type": "json_object"}
        )

        if response.success:
            return response.content
        else:
            logger.error(f"Grievance analysis failed: {response.error}")
            return {
                "error": response.error,
                "category": "other",
                "sentiment": "neutral",
                "urgency": "medium",
                "risk_level": "low"
            }

    async def detect_patterns(
        self,
        grievances: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        if len(grievances) < 2:
            return {"patterns": [], "recurring_issues": False}

        grievances_summary = [
            {
                "id": g.get("id"),
                "category": g.get("category", "unknown"),
                "complaint": g.get("complaint", "")[:200],
                "location": g.get("location", "unknown"),
                "date": str(g.get("created_at", ""))
            }
            for g in grievances[:20]
        ]

        prompt = f"""
Analyze the following grievances to detect patterns and recurring issues.

Grievances Data:
{json.dumps(grievances_summary, indent=2)}

Please provide analysis in JSON format with:
1. patterns: List of detected patterns, each containing:
   - pattern_type: Type of pattern detected
   - description: Description of the pattern
   - affected_grievance_ids: List of related grievance IDs
   - frequency: How often this pattern occurs
   - severity: Severity level of the pattern
2. recurring_issues: Boolean indicating if recurring issues exist
3. similarity_score: Overall similarity score (0-1)
4. geographic_clusters: List of geographic areas with concentrated issues
5. time_patterns: Any time-based patterns detected
6. recommendations: List of recommendations to address patterns
"""

        response = await self.process_async(
            user_input=prompt,
            response_format={"type": "json_object"}
        )

        if response.success:
            return response.content
        else:
            logger.error(f"Pattern detection failed: {response.error}")
            return {"patterns": [], "recurring_issues": False, "error": response.error}

    async def analyze_sentiment(
        self,
        text: str,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        prompt = f"""
Analyze the sentiment of the following text.
Language: {language if language else 'Auto-detect'}

Text:
{text}

Please provide analysis in JSON format with:
1. sentiment: Overall sentiment (positive, negative, neutral)
2. sentiment_score: Score from -1 (very negative) to 1 (very positive)
3. confidence: Confidence in sentiment analysis (0-1)
4. key_phrases: List of key phrases that influenced sentiment
5. emotions: List of detected emotions (anger, frustration, satisfaction, etc.)
6. language_detected: Detected language
7. language_confidence: Confidence in language detection (0-1)
"""

        response = await self.process_async(
            user_input=prompt,
            response_format={"type": "json_object"}
        )

        if response.success:
            return response.content
        else:
            logger.error(f"Sentiment analysis failed: {response.error}")
            return {
                "sentiment": "neutral",
                "sentiment_score": 0,
                "confidence": 0,
                "error": response.error
            }

    async def categorize_grievance(
        self,
        text: str
    ) -> Dict[str, Any]:
        categories = [
            "supply_shortage",
            "delivery_delay",
            "quality_issue",
            "staff_behavior",
            "infrastructure",
            "documentation",
            "beneficiary_issue",
            "corruption",
            "safety",
            "other"
        ]

        prompt = f"""
Categorize the following grievance text.

Available Categories:
{json.dumps(categories)}

Grievance Text:
{text}

Please provide response in JSON format with:
1. category: Best matching category from the list
2. subcategory: More specific subcategory
3. confidence: Confidence in categorization (0-1)
4. alternative_categories: List of other possible categories with confidence scores
5. keywords: List of keywords that influenced categorization
"""

        response = await self.process_async(
            user_input=prompt,
            response_format={"type": "json_object"}
        )

        if response.success:
            return response.content
        else:
            logger.error(f"Categorization failed: {response.error}")
            return {
                "category": "other",
                "subcategory": "general",
                "confidence": 0,
                "error": response.error
            }

    async def assess_risk(
        self,
        grievance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        prompt = f"""
Assess the risk level of the following grievance.

Grievance Details:
{json.dumps(grievance_data, indent=2)}

Please provide risk assessment in JSON format with:
1. risk_level: Overall risk level (critical, high, medium, low)
2. risk_score: Numerical risk score (0-100)
3. risk_factors: List of identified risk factors
4. impact_assessment: Assessment of potential impact
5. urgency: Urgency level (immediate, high, medium, low)
6. escalation_required: Boolean indicating if escalation is required
7. escalation_level: Recommended escalation level (state, district, block)
8. recommended_actions: List of immediate recommended actions
9. timeline: Recommended timeline for resolution
10. confidence: Confidence in risk assessment (0-1)
"""

        response = await self.process_async(
            user_input=prompt,
            response_format={"type": "json_object"}
        )

        if response.success:
            return response.content
        else:
            logger.error(f"Risk assessment failed: {response.error}")
            return {
                "risk_level": "medium",
                "risk_score": 50,
                "risk_factors": [],
                "error": response.error
            }


grievance_intelligence_agent = GrievanceIntelligenceAgent()
