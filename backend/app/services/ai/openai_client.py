import asyncio
from typing import Optional, List, Dict, Any
from openai import AsyncOpenAI, OpenAI
from openai import APIError, APIConnectionError, RateLimitError

from ...config import settings
from ...utils.logger import get_logger

logger = get_logger(__name__)


class OpenAIClient:
    _instance: Optional["OpenAIClient"] = None
    _async_client: Optional[AsyncOpenAI] = None
    _sync_client: Optional[OpenAI] = None

    def __new__(cls) -> "OpenAIClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    @property
    def async_client(self) -> AsyncOpenAI:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured in environment variables")
        if self._async_client is None:
            self._async_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        return self._async_client

    @property
    def sync_client(self) -> OpenAI:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured in environment variables")
        if self._sync_client is None:
            self._sync_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return self._sync_client

    async def async_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        try:
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }
            if max_tokens:
                kwargs["max_tokens"] = max_tokens
            if response_format:
                kwargs["response_format"] = response_format

            response = await self.async_client.chat.completions.create(**kwargs)
            
            logger.info(f"OpenAI API call successful - Model: {model}, Tokens used: {response.usage.total_tokens if response.usage else 'N/A'}")
            
            return {
                "content": response.choices[0].message.content if response.choices else "",
                "role": response.choices[0].message.role if response.choices else "assistant",
                "finish_reason": response.choices[0].finish_reason if response.choices else None,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                } if response.usage else None,
                "model": response.model,
            }
        except RateLimitError as e:
            logger.error(f"Rate limit exceeded: {e}")
            raise
        except APIConnectionError as e:
            logger.error(f"API connection error: {e}")
            raise
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def sync_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        try:
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }
            if max_tokens:
                kwargs["max_tokens"] = max_tokens
            if response_format:
                kwargs["response_format"] = response_format

            response = self.sync_client.chat.completions.create(**kwargs)
            
            logger.info(f"OpenAI API call successful - Model: {model}, Tokens used: {response.usage.total_tokens if response.usage else 'N/A'}")
            
            return {
                "content": response.choices[0].message.content if response.choices else "",
                "role": response.choices[0].message.role if response.choices else "assistant",
                "finish_reason": response.choices[0].finish_reason if response.choices else None,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                } if response.usage else None,
                "model": response.model,
            }
        except RateLimitError as e:
            logger.error(f"Rate limit exceeded: {e}")
            raise
        except APIConnectionError as e:
            logger.error(f"API connection error: {e}")
            raise
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def async_chat_with_retry(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> Dict[str, Any]:
        last_error = None
        for attempt in range(max_retries):
            try:
                return await self.async_chat_completion(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format=response_format,
                )
            except RateLimitError as e:
                last_error = e
                wait_time = retry_delay * (2 ** attempt)
                logger.warning(f"Rate limit hit, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(wait_time)
            except APIConnectionError as e:
                last_error = e
                wait_time = retry_delay * (2 ** attempt)
                logger.warning(f"Connection error, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(wait_time)
        
        raise last_error or Exception("Max retries exceeded")

    @classmethod
    def get_instance(cls) -> "OpenAIClient":
        return cls()


openai_client = OpenAIClient.get_instance()
