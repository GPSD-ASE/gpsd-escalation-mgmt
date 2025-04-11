from contextlib import asynccontextmanager
import redis.asyncio as redis
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache import FastAPICache
from fastapi import FastAPI, Request
import json
import time
from datetime import datetime as dt, timedelta, timezone
from config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB_NAME


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, password= REDIS_PASSWORD,
        db=REDIS_DB_NAME, decode_responses=False, ssl=True)
    FastAPICache.init(RedisBackend(redis_client), prefix="gptapi-cache")
    try:
        yield
    finally:
        redis_client.close()
        await redis_client.wait_closed()


async def log_request_util(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    client_ip = request.client.host
    endpoint = request.url.path
    status_code = response.status_code
    timestamp = dt.now(timezone.utc).isoformat()

    log = {
        "ip": client_ip,
        "endpoint": endpoint,
        "status": status_code,
        "duration": duration,
        "time": timestamp
    }

    redis_client = FastAPICache.get_backend().redis
    await redis_client.lpush("request_logs", json.dumps(log))
    await redis_client.ltrim("request_logs", 0, 999)

    return response
