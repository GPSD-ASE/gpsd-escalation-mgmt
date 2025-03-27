from fastapi import HTTPException
import requests
from datetime import datetime as dt, timedelta
from fastapi_cache.decorator import cache
from config import PREDICTHQ_API_KEY, PREDICTHQ_SEARCH_URL


@cache(expire=1800)
async def get_nearby_events(latitude: float, longitude: float, datetime: str):
    """Fetches ongoing events near the given location using PredictHQ API."""
    headers = {
        "Authorization": f"Bearer {PREDICTHQ_API_KEY}",
        "Accept": "application/json"
    }
    start_datetime = dt.strptime(
        datetime, "%Y-%m-%dT%H:%M:%S") - timedelta(hours=3)
    end_datetime = dt.strptime(
        datetime, "%Y-%m-%dT%H:%M:%S") + timedelta(hours=3)
    end_datetime = f"{end_datetime.strftime('%Y-%m-%dT%H:%M:%S')}Z"
    start_datetime = f"{start_datetime.strftime('%Y-%m-%dT%H:%M:%S')}Z"
    params = {
        "within": f"600m@{latitude},{longitude}",
        "start.gte": start_datetime,
        "start.lte": end_datetime,
        "category": "concerts,festivals,performing-arts,sports,community",
        "limit": 5
    }

    response = requests.get(PREDICTHQ_SEARCH_URL,
                            headers=headers, params=params)
    if response.status_code == 200:
        events = response.json().get("results", [])
        return events
    else:
        raise HTTPException(
            status_code=500, detail="Failed to fetch events from PredictHQ")
