import redis
from ..config import settings
from typing import Optional, Any
import json

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_cache(key: str) -> Optional[Any]:
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception:
        return None


def set_cache(key: str, value: Any, expire: int = 3600) -> bool:
    try:
        redis_client.setex(key, expire, json.dumps(value))
        return True
    except Exception:
        return False


def delete_cache(key: str) -> bool:
    try:
        redis_client.delete(key)
        return True
    except Exception:
        return False


def delete_pattern(pattern: str) -> int:
    try:
        keys = redis_client.keys(pattern)
        if keys:
            return redis_client.delete(*keys)
        return 0
    except Exception:
        return 0
