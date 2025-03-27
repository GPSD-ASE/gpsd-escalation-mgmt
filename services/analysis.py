from models import IncidentRequest
from fastapi import Request, HTTPException
from middleware.gpt import analyze_incident_with_chatgpt
from middleware.predicthq import get_nearby_events


async def incident_analysis(request: Request, body: IncidentRequest):
    """API Endpoint to analyze an incident and determine emergency response needs."""
    try:
        event_data = await get_nearby_events(
            body.latitude, body.longitude, body.datetime)

        incident_data = {
            "latitude": body.latitude,
            "longitude": body.longitude,
            "location_name": body.location_name,
            "incident_type": body.incident_type,
            "datetime": body.datetime
        }

        chatgpt_response = await analyze_incident_with_chatgpt(
            incident_data, event_data)

        return {
            "incident_data": incident_data,
            "event_data": event_data,
            "response": chatgpt_response
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
