from fastapi import APIRouter, Query
from middleware.limiter import limiter
from services.stats import get_stats_json
from fastapi import Request
from typing import Optional
from services.stats import plot_stats
router = APIRouter()


@router.get("/stats/json")
@limiter.limit("5000/minute")
async def stats_json(request: Request, ip: Optional[str] = Query(None),
                     endpoint: Optional[str] = Query(None),
                     since: Optional[str] = Query(None)):
    """API Endpoint to get request logs."""
    return await get_stats_json(ip, endpoint, since)


@router.get("/stats/plot")
@limiter.limit("5000/minute")
async def stats_plot(request: Request):
    """API Endpoint to plot request log."""
    return await plot_stats(request)
