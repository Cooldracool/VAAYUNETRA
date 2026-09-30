# VaayuNetra API Specification

## 1. Principles

-   REST-first for MVP.
-   JSON for structured data.
-   GeoJSON for spatial objects where appropriate.
-   Consistent IDs.
-   Explicit timestamps.
-   Preserve confidence and provenance.
-   Never expose unvalidated claims as facts.

## 2. Events

### GET /api/events

Returns events filtered by: - bounding box, - H3/city/corridor, -
severity, - status, - source category, - confidence, - time range.

### GET /api/events/{event_id}

Returns the complete Environmental Event.

### GET /api/events/{event_id}/evidence

Returns evidence records and provenance.

### GET /api/events/{event_id}/forecast

Returns forecast horizons and affected geometries.

### GET /api/events/{event_id}/risk

Returns exposure and priority components.

## 3. Citizen Reports

### POST /api/citizen-reports

Input:

``` json
{
  "timestamp": "...",
  "latitude": 0,
  "longitude": 0,
  "description": "...",
  "image": "multipart upload"
}
```

Output should contain: - report ID, - status, - CV result if
processed, - linked event if corroborated.

## 4. Sensor Data

### POST /api/sensor-data

Normalized input:

``` json
{
  "sensor_id": "...",
  "timestamp": "...",
  "latitude": 0,
  "longitude": 0,
  "parameter": "pm25",
  "value": 0,
  "unit": "ug/m3",
  "quality_flag": "good"
}
```

## 5. Corridors

### GET /api/corridors/{corridor_id}/events

Returns active/recent events intersecting the corridor.

## 6. Alerts

### GET /api/alerts

Returns alerts visible to the authenticated authority.

### POST /api/events/{event_id}/acknowledge

Marks an alert/event as acknowledged.

### POST /api/events/{event_id}/outcome

Records field verification and outcome.

Example:

``` json
{
  "status": "RESOLVED",
  "verified_source": "OPEN_BURNING",
  "notes": "...",
  "action_taken": "..."
}
```

## 7. Event Contract

``` json
{
  "event_id": "EVT-1024",
  "created_at": "...",
  "geometry": {},
  "severity": "HIGH",
  "confidence": 0.87,
  "priority": 89,
  "pollutants": [],
  "evidence": [],
  "source_hypotheses": [],
  "forecasts": [],
  "exposure": {},
  "jurisdiction": {},
  "recommended_actions": [],
  "status": "ACTIVE"
}
```

## 8. Error Handling

Use clear HTTP status codes.

Errors should contain:

``` json
{
  "error": {
    "code": "...",
    "message": "...",
    "details": {}
  }
}
```

Do not leak secrets or internal stack traces.

## 9. Versioning

Prefer `/api/v1/...` once external clients depend on the API.

Keep backward compatibility for stable contracts.
