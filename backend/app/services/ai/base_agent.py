from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime
import json

from .openai_client import OpenAIClient
from ...utils.logger import get_logger

logger = get_logger(__name__)


class AgentStatus(str, Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    COMPLETED = "completed"


class AgentResponse:
    def __init__(
        self,
        success: bool,
        content: Any,
        agent_name: str,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ):
        self.success = success
        self.content = content
        self.agent_name = agent_name
        self.metadata = metadata or {}
        self.error = error
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "content": self.content,
            "agent_name": self.agent_name,
            "metadata": self.metadata,
            "error": self.error,
            "timestamp": self.timestamp,
        }


class BaseAIAgent(ABC):
    def __init__(
        self,
        agent_name: str,
        system_prompt: str,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ):
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.status = AgentStatus.IDLE
        self._client: Optional[OpenAIClient] = None
        self._conversation_history: List[Dict[str, str]] = []

    @property
    def client(self) -> OpenAIClient:
        if self._client is None:
            self._client = OpenAIClient.get_instance()
        return self._client

    def _build_messages(self, user_input: str, include_history: bool = False) -> List[Dict[str, str]]:
        messages = [{"role": "system", "content": self.system_prompt}]
        
        if include_history and self._conversation_history:
            messages.extend(self._conversation_history)
        
        messages.append({"role": "user", "content": user_input})
        
        return messages

    def _add_to_history(self, role: str, content: str, max_history: int = 10):
        self._conversation_history.append({"role": role, "content": content})
        
        if len(self._conversation_history) > max_history:
            self._conversation_history = self._conversation_history[-max_history:]

    def clear_history(self):
        self._conversation_history = []
        logger.info(f"Conversation history cleared for agent: {self.agent_name}")

    async def process_async(
        self,
        user_input: str,
        include_history: bool = False,
        response_format: Optional[Dict[str, str]] = None,
    ) -> AgentResponse:
        self.status = AgentStatus.PROCESSING
        logger.info(f"Agent {self.agent_name} started processing")

        try:
            messages = self._build_messages(user_input, include_history)
            
            response = await self.client.async_chat_with_retry(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format=response_format,
            )

            content = response.get("content", "")
            
            self._add_to_history("user", user_input)
            self._add_to_history("assistant", content)

            parsed_content = self._parse_response(content)
            
            self.status = AgentStatus.COMPLETED
            logger.info(f"Agent {self.agent_name} completed processing successfully")

            return AgentResponse(
                success=True,
                content=parsed_content,
                agent_name=self.agent_name,
                metadata={
                    "model": response.get("model"),
                    "usage": response.get("usage"),
                    "finish_reason": response.get("finish_reason"),
                },
            )

        except Exception as e:
            self.status = AgentStatus.ERROR
            logger.error(f"Agent {self.agent_name} encountered an error: {str(e)}")
            
            return AgentResponse(
                success=False,
                content=None,
                agent_name=self.agent_name,
                error=str(e),
            )

    def process_sync(
        self,
        user_input: str,
        include_history: bool = False,
        response_format: Optional[Dict[str, str]] = None,
    ) -> AgentResponse:
        self.status = AgentStatus.PROCESSING
        logger.info(f"Agent {self.agent_name} started processing (sync)")

        try:
            messages = self._build_messages(user_input, include_history)
            
            response = self.client.sync_chat_completion(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format=response_format,
            )

            content = response.get("content", "")
            
            self._add_to_history("user", user_input)
            self._add_to_history("assistant", content)

            parsed_content = self._parse_response(content)
            
            self.status = AgentStatus.COMPLETED
            logger.info(f"Agent {self.agent_name} completed processing successfully (sync)")

            return AgentResponse(
                success=True,
                content=parsed_content,
                agent_name=self.agent_name,
                metadata={
                    "model": response.get("model"),
                    "usage": response.get("usage"),
                    "finish_reason": response.get("finish_reason"),
                },
            )

        except Exception as e:
            self.status = AgentStatus.ERROR
            logger.error(f"Agent {self.agent_name} encountered an error: {str(e)}")
            
            return AgentResponse(
                success=False,
                content=None,
                agent_name=self.agent_name,
                error=str(e),
            )

    def _parse_response(self, content: str) -> Any:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return content

    @abstractmethod
    def analyze(self, *args, **kwargs) -> AgentResponse:
        pass

    @abstractmethod
    def get_recommendations(self, *args, **kwargs) -> AgentResponse:
        pass

    def get_status(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "status": self.status.value,
            "model": self.model,
            "conversation_history_length": len(self._conversation_history),
        }
