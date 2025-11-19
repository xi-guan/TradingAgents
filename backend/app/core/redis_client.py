"""Redis 客户端管理"""

import json
from typing import Optional, Any
from redis.asyncio import Redis, ConnectionPool
from app.config import settings

# Redis 连接池
redis_pool: Optional[ConnectionPool] = None
redis_client: Optional[Redis] = None


async def init_redis():
    """初始化 Redis 连接"""
    global redis_pool, redis_client

    redis_pool = ConnectionPool.from_url(
        settings.redis_url,
        password=settings.redis_password,
        encoding="utf-8",
        decode_responses=True,
        max_connections=50,
    )

    redis_client = Redis(connection_pool=redis_pool)

    # 测试连接
    await redis_client.ping()


async def close_redis():
    """关闭 Redis 连接"""
    if redis_client:
        await redis_client.close()
    if redis_pool:
        await redis_pool.disconnect()


async def get_redis() -> Redis:
    """获取 Redis 客户端（依赖注入）"""
    return redis_client


class RedisCache:
    """Redis 缓存工具类"""

    def __init__(self, client: Redis):
        self.client = client

    async def get(self, key: str) -> Optional[str]:
        """获取缓存"""
        return await self.client.get(key)

    async def set(
        self,
        key: str,
        value: Any,
        ex: Optional[int] = None
    ) -> bool:
        """设置缓存"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        return await self.client.set(key, value, ex=ex)

    async def get_json(self, key: str) -> Optional[dict]:
        """获取 JSON 缓存"""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None

    async def delete(self, key: str) -> int:
        """删除缓存"""
        return await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return await self.client.exists(key) > 0

    async def expire(self, key: str, seconds: int) -> bool:
        """设置过期时间"""
        return await self.client.expire(key, seconds)

    async def ttl(self, key: str) -> int:
        """获取剩余过期时间"""
        return await self.client.ttl(key)


# 缓存键命名规范
class CacheKeys:
    """缓存键定义"""

    # 实时行情（TTL: 5分钟）
    STOCK_QUOTE = "quote:{market}:{symbol}"

    # 股票基本信息（TTL: 1天）
    STOCK_INFO = "info:{market}:{symbol}"

    # 用户会话（TTL: 7天）
    USER_SESSION = "session:{user_id}"

    # 分析任务进度（TTL: 24小时）
    TASK_PROGRESS = "task:{task_id}:progress"

    # API 速率限制（TTL: 1分钟）
    RATE_LIMIT = "ratelimit:{user_id}:{endpoint}"

    @classmethod
    def quote_key(cls, market: str, symbol: str) -> str:
        return cls.STOCK_QUOTE.format(market=market, symbol=symbol)

    @classmethod
    def info_key(cls, market: str, symbol: str) -> str:
        return cls.STOCK_INFO.format(market=market, symbol=symbol)

    @classmethod
    def session_key(cls, user_id: str) -> str:
        return cls.USER_SESSION.format(user_id=user_id)

    @classmethod
    def task_key(cls, task_id: str) -> str:
        return cls.TASK_PROGRESS.format(task_id=task_id)

    @classmethod
    def rate_limit_key(cls, user_id: str, endpoint: str) -> str:
        return cls.RATE_LIMIT.format(user_id=user_id, endpoint=endpoint)
