import json
from fastapi_cache import FastAPICache
from typing import Optional
from fastapi import Query, Request
import matplotlib.pyplot as plt
import io
from fastapi.responses import StreamingResponse
from collections import Counter


async def get_stats_json(request: Request,
                         ip: Optional[str] = Query(None),
                         endpoint: Optional[str] = Query(None),
                         since: Optional[str] = Query(None)
                         ):
    redis_client = FastAPICache.get_backend().redis
    logs = await redis_client.lrange("request_logs", 0, 1000)
    parsed_logs = [json.loads(log) for log in logs]

    if ip:
        parsed_logs = [log for log in parsed_logs if log["ip"] == ip]
    if endpoint:
        parsed_logs = [
            log for log in parsed_logs if log["endpoint"] == endpoint]
    if since:
        parsed_logs = [
            log for log in parsed_logs
            if log["time"] >= since
        ]

    return {"count": len(parsed_logs), "requests": parsed_logs}


async def plot_stats():
    redis_client = FastAPICache.get_backend().redis
    logs = await redis_client.lrange("request_logs", 0, 1000)
    parsed_logs = [json.loads(log) for log in logs]

    endpoint_counts = Counter(log["endpoint"] for log in parsed_logs)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(endpoint_counts.keys(), endpoint_counts.values())
    ax.set_title("Requests per Endpoint")
    ax.set_ylabel("Count")
    plt.xticks(rotation=45)

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")
