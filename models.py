from typing import Optional
from pydantic import BaseModel


class IncidentRequest(BaseModel):
    latitude: float
    longitude: float
    location_name: str
    incident_type: str
    datetime: str
