from fastapi import APIRouter
from middleware.limiter import limiter
from services.analysis import incident_analysis
from models import IncidentRequest
from fastapi import Request
router = APIRouter()


@router.post("/incident-analysis/")
@limiter.limit("5/minute")
async def incident_escalation(request: Request, body: IncidentRequest):
    """API Endpoint to analyze an incident and determine emergency response needs."""
    return await incident_analysis(request, body)
