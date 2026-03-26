import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from abc import ABC

from app.services.ai.base_agent import BaseAIAgent, AgentStatus, AgentResponse
from app.services.ai.agents.recommendation_engine import (
    RecommendationEngine,
    RecommendationPriority,
    RecommendationCategory,
    recommendation_engine,
)
from app.services.ai.agents.compliance_audit import (
    ComplianceAuditAgent,
    ComplianceStatus,
    AuditAction,
    compliance_audit_agent,
)
from app.services.ai.agents.community_coordination import (
    CommunityCoordinationAgent,
    MeetingStatus,
    NotificationType,
    community_coordination_agent,
)
from app.services.ai.agents.integration_agent import (
    IntegrationAgent,
    IntegrationType,
    SyncStatus,
    integration_agent,
)


class ConcreteAIAgent(BaseAIAgent):
    def analyze(self, *args, **kwargs):
        return AgentResponse(
            success=True,
            content={"result": "analysis_complete"},
            agent_name=self.agent_name,
        )

    def get_recommendations(self, *args, **kwargs):
        return AgentResponse(
            success=True,
            content={"recommendations": []},
            agent_name=self.agent_name,
        )


class TestAgentStatus:
    def test_agent_status_values(self):
        assert AgentStatus.IDLE.value == "idle"
        assert AgentStatus.PROCESSING.value == "processing"
        assert AgentStatus.ERROR.value == "error"
        assert AgentStatus.COMPLETED.value == "completed"

    def test_agent_status_is_string_enum(self):
        assert isinstance(AgentStatus.IDLE, str)
        assert AgentStatus.IDLE == "idle"


class TestAgentResponse:
    def test_agent_response_creation(self):
        response = AgentResponse(
            success=True,
            content="test content",
            agent_name="TestAgent",
        )
        assert response.success is True
        assert response.content == "test content"
        assert response.agent_name == "TestAgent"
        assert response.error is None

    def test_agent_response_with_error(self):
        response = AgentResponse(
            success=False,
            content=None,
            agent_name="TestAgent",
            error="Something went wrong",
        )
        assert response.success is False
        assert response.error == "Something went wrong"

    def test_agent_response_to_dict(self):
        response = AgentResponse(
            success=True,
            content={"key": "value"},
            agent_name="TestAgent",
            metadata={"model": "gpt-4"},
        )
        result = response.to_dict()
        assert isinstance(result, dict)
        assert result["success"] is True
        assert result["agent_name"] == "TestAgent"
        assert result["metadata"]["model"] == "gpt-4"
        assert "timestamp" in result

    def test_agent_response_with_metadata(self):
        response = AgentResponse(
            success=True,
            content="result",
            agent_name="TestAgent",
            metadata={"tokens": 100, "model": "gpt-4"},
        )
        assert response.metadata["tokens"] == 100
        assert response.metadata["model"] == "gpt-4"


class TestBaseAIAgent:
    def test_base_ai_agent_is_abstract(self):
        assert issubclass(BaseAIAgent, ABC)

    def test_base_ai_agent_instantiation_with_concrete_class(self):
        agent = ConcreteAIAgent(
            agent_name="TestAgent",
            system_prompt="You are a test agent.",
        )
        assert agent.agent_name == "TestAgent"
        assert agent.system_prompt == "You are a test agent."
        assert agent.status == AgentStatus.IDLE

    def test_base_ai_agent_default_model(self):
        agent = ConcreteAIAgent(
            agent_name="TestAgent",
            system_prompt="Test prompt",
        )
        assert agent.model == "gpt-4-turbo-preview"

    def test_base_ai_agent_custom_model(self):
        agent = ConcreteAIAgent(
            agent_name="TestAgent",
            system_prompt="Test prompt",
            model="gpt-3.5-turbo",
        )
        assert agent.model == "gpt-3.5-turbo"

    def test_base_ai_agent_temperature(self):
        agent = ConcreteAIAgent(
            agent_name="TestAgent",
            system_prompt="Test prompt",
            temperature=0.5,
        )
        assert agent.temperature == 0.5

    def test_base_ai_agent_default_temperature(self):
        agent = ConcreteAIAgent(
            agent_name="TestAgent",
            system_prompt="Test prompt",
        )
        assert agent.temperature == 0.7

    def test_base_ai_agent_max_tokens(self):
        agent = ConcreteAIAgent(
            agent_name="TestAgent",
            system_prompt="Test prompt",
            max_tokens=1000,
        )
        assert agent.max_tokens == 1000

    def test_base_ai_agent_conversation_history_initialization(self):
        agent = ConcreteAIAgent(
            agent_name="TestAgent",
            system_prompt="Test prompt",
        )
        assert agent._conversation_history == []

    def test_base_ai_agent_clear_history(self):
        agent = ConcreteAIAgent(
            agent_name="TestAgent",
            system_prompt="Test prompt",
        )
        agent._conversation_history.append({"role": "user", "content": "test"})
        agent.clear_history()
        assert agent._conversation_history == []

    def test_base_ai_agent_get_status(self):
        agent = ConcreteAIAgent(
            agent_name="TestAgent",
            system_prompt="Test prompt",
        )
        status = agent.get_status()
        assert status["agent_name"] == "TestAgent"
        assert status["status"] == "idle"
        assert status["model"] == "gpt-4-turbo-preview"
        assert status["conversation_history_length"] == 0

    def test_base_ai_agent_build_messages(self):
        agent = ConcreteAIAgent(
            agent_name="TestAgent",
            system_prompt="System prompt here",
        )
        messages = agent._build_messages("User input")
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "System prompt here"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "User input"

    def test_base_ai_agent_build_messages_with_history(self):
        agent = ConcreteAIAgent(
            agent_name="TestAgent",
            system_prompt="System prompt",
        )
        agent._conversation_history = [
            {"role": "user", "content": "Previous input"},
            {"role": "assistant", "content": "Previous response"},
        ]
        messages = agent._build_messages("New input", include_history=True)
        assert len(messages) == 4


class TestBaseAIAgentOpenAIClient:
    def test_client_property_lazy_initialization(self):
        agent = ConcreteAIAgent(
            agent_name="TestAgent",
            system_prompt="Test prompt",
        )
        assert agent._client is None

    @patch("app.services.ai.base_agent.OpenAIClient")
    def test_client_get_instance_called(self, mock_openai_client):
        mock_instance = MagicMock()
        mock_openai_client.get_instance.return_value = mock_instance
        agent = ConcreteAIAgent(
            agent_name="TestAgent",
            system_prompt="Test prompt",
        )
        agent._client = None
        client = agent.client
        mock_openai_client.get_instance.assert_called_once()


class TestRecommendationEngine:
    def test_recommendation_engine_instantiation(self):
        engine = RecommendationEngine()
        assert engine.agent_name == "RecommendationEngine"
        assert engine.model == "gpt-4-turbo-preview"
        assert engine.temperature == 0.4
        assert engine.recommendations_store == []

    def test_recommendation_engine_is_base_ai_agent_subclass(self):
        assert issubclass(RecommendationEngine, BaseAIAgent)

    def test_recommendation_engine_has_system_prompt(self):
        engine = RecommendationEngine()
        assert "Recommendation Engine" in engine.system_prompt

    def test_recommendation_priority_enum(self):
        assert RecommendationPriority.CRITICAL.value == "critical"
        assert RecommendationPriority.HIGH.value == "high"
        assert RecommendationPriority.MEDIUM.value == "medium"
        assert RecommendationPriority.LOW.value == "low"

    def test_recommendation_category_enum(self):
        assert RecommendationCategory.SUPPLY_OPTIMIZATION.value == "supply_optimization"
        assert RecommendationCategory.ROUTE_IMPROVEMENT.value == "route_improvement"
        assert RecommendationCategory.INVENTORY_MANAGEMENT.value == "inventory_management"

    def test_get_fallback_recommendations(self):
        engine = RecommendationEngine()
        recommendations = engine._get_fallback_recommendations("admin")
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    def test_calculate_priority_score(self):
        engine = RecommendationEngine()
        recommendation = {
            "priority": "high",
            "impact": "high",
            "effort": "low",
            "confidence": 0.9,
        }
        score = engine.calculate_priority_score(recommendation)
        assert isinstance(score, float)
        assert 0 <= score <= 100

    def test_get_all_recommendations(self):
        engine = RecommendationEngine()
        engine.recommendations_store = [{"id": "1", "title": "Test"}]
        all_recs = engine.get_all_recommendations()
        assert len(all_recs) == 1

    def test_update_recommendation_status(self):
        engine = RecommendationEngine()
        engine.recommendations_store = [{"id": "rec-001", "status": "pending"}]
        result = engine.update_recommendation_status("rec-001", "completed")
        assert result is not None
        assert result["status"] == "completed"

    def test_update_recommendation_status_not_found(self):
        engine = RecommendationEngine()
        result = engine.update_recommendation_status("nonexistent", "completed")
        assert result is None

    def test_global_recommendation_engine_instance(self):
        assert recommendation_engine is not None
        assert isinstance(recommendation_engine, RecommendationEngine)


class TestComplianceAuditAgent:
    def test_compliance_audit_agent_instantiation(self):
        agent = ComplianceAuditAgent()
        assert agent.agent_name == "ComplianceAuditAgent"
        assert agent.model == "gpt-4-turbo-preview"
        assert agent.temperature == 0.2
        assert agent.audit_logs == []

    def test_compliance_audit_agent_is_base_ai_agent_subclass(self):
        assert issubclass(ComplianceAuditAgent, BaseAIAgent)

    def test_compliance_status_enum(self):
        assert ComplianceStatus.COMPLIANT.value == "compliant"
        assert ComplianceStatus.NON_COMPLIANT.value == "non_compliant"
        assert ComplianceStatus.PARTIAL.value == "partial"
        assert ComplianceStatus.PENDING_REVIEW.value == "pending_review"

    def test_audit_action_enum(self):
        assert AuditAction.CREATE.value == "create"
        assert AuditAction.UPDATE.value == "update"
        assert AuditAction.DELETE.value == "delete"
        assert AuditAction.VIEW.value == "view"

    def test_log_action(self):
        agent = ComplianceAuditAgent()
        log_entry = agent.log_action(
            user_id=1,
            action="create",
            entity_type="delivery",
            entity_id=100,
        )
        assert log_entry["user_id"] == 1
        assert log_entry["action"] == "create"
        assert log_entry["entity_type"] == "delivery"
        assert log_entry["entity_id"] == 100
        assert "id" in log_entry
        assert "timestamp" in log_entry

    def test_log_action_adds_to_audit_logs(self):
        agent = ComplianceAuditAgent()
        initial_count = len(agent.audit_logs)
        agent.log_action(user_id=1, action="view", entity_type="user")
        assert len(agent.audit_logs) == initial_count + 1

    def test_get_audit_logs(self):
        agent = ComplianceAuditAgent()
        agent.log_action(user_id=1, action="create", entity_type="delivery")
        agent.log_action(user_id=2, action="update", entity_type="delivery")
        logs = agent.get_audit_logs()
        assert len(logs) == 2

    def test_get_audit_logs_filter_by_user(self):
        agent = ComplianceAuditAgent()
        agent.log_action(user_id=1, action="create", entity_type="delivery")
        agent.log_action(user_id=2, action="update", entity_type="delivery")
        logs = agent.get_audit_logs(user_id=1)
        assert len(logs) == 1
        assert logs[0]["user_id"] == 1

    def test_get_compliance_status(self):
        agent = ComplianceAuditAgent()
        status = agent.get_compliance_status()
        assert "total_audit_entries" in status
        assert "last_audit" in status
        assert "compliance_records_count" in status

    def test_get_fallback_report(self):
        agent = ComplianceAuditAgent()
        report = agent._get_fallback_report(district_id=1, total_actions=10)
        assert report["district_id"] == 1
        assert report["total_actions_audited"] == 10
        assert "overall_status" in report
        assert "compliance_score" in report

    def test_global_compliance_audit_agent_instance(self):
        assert compliance_audit_agent is not None
        assert isinstance(compliance_audit_agent, ComplianceAuditAgent)


class TestCommunityCoordinationAgent:
    def test_community_coordination_agent_instantiation(self):
        agent = CommunityCoordinationAgent()
        assert agent.agent_name == "CommunityCoordinationAgent"
        assert agent.model == "gpt-4-turbo-preview"
        assert agent.temperature == 0.3
        assert agent.stakeholders == []
        assert agent.connections == []
        assert agent.meetings == []
        assert agent.notifications == []

    def test_community_coordination_agent_is_base_ai_agent_subclass(self):
        assert issubclass(CommunityCoordinationAgent, BaseAIAgent)

    def test_meeting_status_enum(self):
        assert MeetingStatus.SCHEDULED.value == "scheduled"
        assert MeetingStatus.IN_PROGRESS.value == "in_progress"
        assert MeetingStatus.COMPLETED.value == "completed"
        assert MeetingStatus.CANCELLED.value == "cancelled"

    def test_notification_type_enum(self):
        assert NotificationType.MEETING_INVITE.value == "meeting_invite"
        assert NotificationType.TASK_ASSIGNMENT.value == "task_assignment"
        assert NotificationType.SYSTEM_ALERT.value == "system_alert"

    def test_register_stakeholder(self):
        agent = CommunityCoordinationAgent()
        stakeholder_data = {
            "name": "John Doe",
            "type": "cdpo",
            "department": "Health",
            "role": "Officer",
        }
        stakeholder = agent.register_stakeholder(stakeholder_data)
        assert stakeholder["name"] == "John Doe"
        assert stakeholder["type"] == "cdpo"
        assert "id" in stakeholder
        assert "registered_at" in stakeholder

    def test_create_connection(self):
        agent = CommunityCoordinationAgent()
        connection = agent.create_connection(
            stakeholder_1_id="s1",
            stakeholder_2_id="s2",
            connection_type="collaboration",
            strength=0.8,
        )
        assert connection["source"] == "s1"
        assert connection["target"] == "s2"
        assert connection["type"] == "collaboration"
        assert connection["strength"] == 0.8

    def test_get_stakeholder_network(self):
        agent = CommunityCoordinationAgent()
        agent.register_stakeholder({"id": "s1", "name": "Stakeholder 1"})
        agent.register_stakeholder({"id": "s2", "name": "Stakeholder 2"})
        agent.create_connection("s1", "s2", "collaboration")
        network = agent.get_stakeholder_network()
        assert "stakeholders" in network
        assert "connections" in network
        assert "stats" in network

    def test_get_notifications(self):
        agent = CommunityCoordinationAgent()
        agent.notifications = [
            {"id": "n1", "recipient_id": "user1", "read": False},
            {"id": "n2", "recipient_id": "user1", "read": True},
        ]
        notifications = agent.get_notifications("user1")
        assert len(notifications) == 2

    def test_get_notifications_unread_only(self):
        agent = CommunityCoordinationAgent()
        agent.notifications = [
            {"id": "n1", "recipient_id": "user1", "read": False},
            {"id": "n2", "recipient_id": "user1", "read": True},
        ]
        notifications = agent.get_notifications("user1", unread_only=True)
        assert len(notifications) == 1
        assert notifications[0]["id"] == "n1"

    def test_mark_notification_read(self):
        agent = CommunityCoordinationAgent()
        agent.notifications = [{"id": "n1", "recipient_id": "user1", "read": False}]
        result = agent.mark_notification_read("n1")
        assert result is not None
        assert result["read"] is True

    def test_mark_notification_read_not_found(self):
        agent = CommunityCoordinationAgent()
        result = agent.mark_notification_read("nonexistent")
        assert result is None

    def test_global_community_coordination_agent_instance(self):
        assert community_coordination_agent is not None
        assert isinstance(community_coordination_agent, CommunityCoordinationAgent)


class TestIntegrationAgent:
    def test_integration_agent_instantiation(self):
        agent = IntegrationAgent()
        assert agent.agent_name == "IntegrationAgent"
        assert agent.model == "gpt-4-turbo-preview"
        assert agent.temperature == 0.2
        assert agent.sync_queue == []

    def test_integration_agent_is_base_ai_agent_subclass(self):
        assert issubclass(IntegrationAgent, BaseAIAgent)

    def test_integration_type_enum(self):
        assert IntegrationType.POSHAN_TRACKER.value == "poshan_tracker"
        assert IntegrationType.ICDS_CAS.value == "icds_cas"
        assert IntegrationType.WEATHER.value == "weather"
        assert IntegrationType.ROAD_INFRASTRUCTURE.value == "road_infrastructure"

    def test_sync_status_enum(self):
        assert SyncStatus.PENDING.value == "pending"
        assert SyncStatus.IN_PROGRESS.value == "in_progress"
        assert SyncStatus.COMPLETED.value == "completed"
        assert SyncStatus.FAILED.value == "failed"

    def test_integration_configs_initialized(self):
        agent = IntegrationAgent()
        assert IntegrationType.POSHAN_TRACKER.value in agent.integration_configs
        assert IntegrationType.ICDS_CAS.value in agent.integration_configs

    def test_get_integration_config(self):
        agent = IntegrationAgent()
        config = agent.get_integration_config(IntegrationType.POSHAN_TRACKER.value)
        assert config is not None
        assert "name" in config
        assert "base_url" in config

    def test_get_integration_config_not_found(self):
        agent = IntegrationAgent()
        config = agent.get_integration_config("nonexistent")
        assert config is None

    def test_get_all_integrations(self):
        agent = IntegrationAgent()
        integrations = agent.get_all_integrations()
        assert isinstance(integrations, list)
        assert len(integrations) > 0

    def test_get_sync_status(self):
        agent = IntegrationAgent()
        agent.sync_queue = [{"id": "sync-1", "status": "completed"}]
        sync = agent.get_sync_status("sync-1")
        assert sync is not None
        assert sync["id"] == "sync-1"

    def test_get_sync_status_not_found(self):
        agent = IntegrationAgent()
        sync = agent.get_sync_status("nonexistent")
        assert sync is None

    def test_get_pending_syncs(self):
        agent = IntegrationAgent()
        agent.sync_queue = [
            {"id": "sync-1", "status": SyncStatus.PENDING.value, "integration_type": "poshan_tracker"},
            {"id": "sync-2", "status": SyncStatus.COMPLETED.value, "integration_type": "poshan_tracker"},
        ]
        pending = agent.get_pending_syncs()
        assert len(pending) == 1
        assert pending[0]["id"] == "sync-1"

    def test_global_integration_agent_instance(self):
        assert integration_agent is not None
        assert isinstance(integration_agent, IntegrationAgent)


class TestAgentInitializationWithOpenAI:
    @patch("app.services.ai.base_agent.OpenAIClient")
    def test_agent_client_initialization(self, mock_openai_client):
        mock_instance = MagicMock()
        mock_openai_client.get_instance.return_value = mock_instance
        agent = ConcreteAIAgent(
            agent_name="TestAgent",
            system_prompt="Test prompt",
        )
        client = agent.client
        mock_openai_client.get_instance.assert_called_once()
        assert client == mock_instance

    def test_agent_client_caching(self):
        agent = ConcreteAIAgent(
            agent_name="TestAgent",
            system_prompt="Test prompt",
        )
        agent._client = MagicMock()
        client1 = agent.client
        client2 = agent.client
        assert client1 == client2
