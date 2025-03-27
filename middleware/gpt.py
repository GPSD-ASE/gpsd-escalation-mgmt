from fastapi import HTTPException
import openai
import json
from fastapi_cache.decorator import cache
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


@cache(expire=1800)
async def analyze_incident_with_chatgpt(incident_data, event_data):
    """Sends the incident and event data to ChatGPT for emergency response estimation."""
    prompt = f"""
You are an emergency response estimator.

Use the following input data to estimate emergency response needs.

Incident Details:
- Location: {incident_data['location_name']}
- Coordinates: ({incident_data['latitude']}, {incident_data['longitude']})
- Incident Type: {incident_data['incident_type']}
- Date & Time: {incident_data['datetime']}

Nearby Events:
{event_data if event_data else "No events nearby."}

Instructions:
1. Base your estimates on the severity of the incident type and the presence (or absence) of nearby events.
2. If there are no nearby events, assume standard local population impact.
3. If there are nearby events, assume higher crowd density and scale up emergency response accordingly.
4. Do not invent any event information.
5. Be consistent for the same inputs.

Return only the following response in **raw JSON** format (no markdown or explanation):

{{
  "affected_people": <estimated number>,
  "required_police_officers": <estimated number>,
  "required_ambulances": <estimated number>,
  "required_fire_brigades": <estimated number>
}}
"""
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[{"role": "system", "content": "You are an emergency response estimator."},
                  {"role": "user", "content": prompt}]
    )

    raw_response = response.choices[0].message
    raw_response = raw_response.content
    if raw_response.startswith("```json"):
        raw_response = raw_response.strip("```json").strip("`").strip()
    elif raw_response.startswith("```"):
        raw_response = raw_response.strip("```").strip()
    try:
        parsed_response = json.loads(raw_response)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500, detail="Invalid JSON response from ChatGPT")

    return parsed_response
