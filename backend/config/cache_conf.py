import json
from typing import Any

import redis.asyncio as redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)


async def get_cache(key: str):
    """
    获取缓存
    """
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败: {e}")
        return None

async def get_json_cache(key: str):
    """
    获取JSON缓存
    """
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(f"获取JSON缓存失败: {e}")
        return None

async def set_cache(key: str, value: Any, expire: int = 3600):
    """
    设置缓存
    """
    try:
        data = json.dumps(value, ensure_ascii=False)
        await redis_client.setex(key, expire, data)
        return True
    except Exception as e:
        print(f"设置缓存失败: {e}")
        return False


async def delete_cache(key: str):
    """
    删除单个缓存
    """
    try:
        return await redis_client.delete(key)
    except Exception as e:
        print(f"删除缓存失败: {e}")
        return 0


async def delete_cache_pattern(pattern: str):
    """
    按模式删除缓存
    """
    try:
        keys = [key async for key in redis_client.scan_iter(match=pattern)]
        if not keys:
            return 0
        return await redis_client.delete(*keys)
    except Exception as e:
        print(f"按模式删除缓存失败: {e}")
        return 0
