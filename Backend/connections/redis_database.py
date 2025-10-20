import redis.asyncio as redis
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

redis_client = None

async def init_redis():
    global redis_client
    try:
        redis_client = await redis.from_url(
            f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
            encoding="utf8",
            decode_responses=True
        )
        await redis_client.ping()
        print(f"✅ Connected to Redis: {REDIS_HOST}:{REDIS_PORT}")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("⚠️  Running without Redis caching")

async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
        print("✅ Redis connection closed")

def get_redis():
    return redis_client

async def cache_set(key: str, value: str, ex: int = 3600):
    """Set cache with expiration"""
    if redis_client:
        try:
            await redis_client.setex(key, ex, value)
        except Exception as e:
            print(f"Cache set error: {e}")

async def cache_get(key: str):
    """Get from cache"""
    if redis_client:
        try:
            return await redis_client.get(key)
        except Exception as e:
            print(f"Cache get error: {e}")
    return None

async def cache_delete(key: str):
    """Delete from cache"""
    if redis_client:
        try:
            await redis_client.delete(key)
        except Exception as e:
            print(f"Cache delete error: {e}")