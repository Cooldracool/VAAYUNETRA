from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# --- GeoJSON Models (RFC 7946) ---
class GeoJSONGeometry(BaseModel):
    type: str = Field(..., description="Geometry type (Point, Polygon, MultiPolygon)")
    coordinates: Any = Field(..., description="GeoJSON coordinates array")


class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: GeoJSONGeometry
    properties: Dict[str, Any] = Field(default_factory=dict)


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature] = Field(default_factory=list)


# --- Feed Models (Citizen Home Radar) ---
class NearbySensor(BaseModel):
    sensor_id: str
    name: str
    latitude: float
    longitude: float
    distance_km: float
    pm25: float
    aqi: int
    quality_flag: str = "good"
    observed_at: str


class ActiveWarning(BaseModel):
    incident_id: str
    category: str
    severity: str
    inside_plume: bool = True
    distance_meters: float
    direction_from_user: str
    message: str
    hindi_message: Optional[str] = None
    punjabi_message: Optional[str] = None


class FeedWeather(BaseModel):
    wind_speed_mps: float
    wind_direction_deg: float
    wind_cardinal: str
    temperature_c: float
    relative_humidity: float
    source: str = "Open-Meteo High-Resolution"


class FeedResponse(BaseModel):
    latitude: float
    longitude: float
    current_pm25: float
    aqi: int
    aqi_category: str
    dominant_pollutant: str = "PM2.5"
    nearby_sensors: List[NearbySensor] = Field(default_factory=list)
    active_warnings: List[ActiveWarning] = Field(default_factory=list)
    weather: FeedWeather
    recommendations: List[str] = Field(default_factory=list)


# --- Incident Reporting & Unified Ticket ---
class AIVisionResult(BaseModel):
    confidence: float
    detected_category: str
    visual_evidence: bool
    model_version: str = "Google-Gemini-1.5-Flash"
    details: Optional[str] = None
    reasoning: Optional[str] = None
    plume_density: Optional[str] = None
    ai_engine: Optional[str] = "Google Gemini Multimodal"
    recommended_authority: Optional[str] = None


class SatelliteThermalMatch(BaseModel):
    matched: bool
    confidence: Optional[float] = None
    satellite_source: str = "NASA FIRMS (VIIRS/MODIS)"
    brightness_temp_k: Optional[float] = None
    frp_mw: Optional[float] = None
    distance_km: Optional[float] = None
    detected_at: Optional[str] = None


class WindVector(BaseModel):
    speed_mps: float
    direction_deg: float
    cardinal: str
    source: str = "Open-Meteo High-Resolution"


class ImpactedReceptor(BaseModel):
    name: str
    type: str  # "school", "hospital", "residential", "care_home"
    latitude: float
    longitude: float
    distance_m: float
    estimated_arrival_minutes: int


class IncidentTicketResponse(BaseModel):
    ticket_id: str
    created_at: str
    status: str = "VERIFIED"
    category: str
    latitude: float
    longitude: float
    ai_vision: AIVisionResult
    satellite_thermal_match: SatelliteThermalMatch
    wind_vector: WindVector
    plume_geometry: GeoJSONGeometry
    impacted_receptors: List[ImpactedReceptor] = Field(default_factory=list)
    severity: str  # "LOW", "MODERATE", "HIGH", "CRITICAL"
    priority_score: int  # 0 to 100
    recommended_action: str
    assigned_authority: str


# --- Simulation Request ---
class SimulateSpikeRequest(BaseModel):
    latitude: Optional[float] = Field(28.6139, description="Target latitude (default: New Delhi)")
    longitude: Optional[float] = Field(77.2090, description="Target longitude")
    category: Optional[str] = Field("waste_burning", description="Source category")
    severity: Optional[str] = Field("HIGH", description="Incident severity level")
    intensity_multiplier: Optional[float] = Field(2.5, description="Spike magnitude multiplier")
    wind_speed_mps: Optional[float] = Field(4.2, description="Wind speed in m/s")
    wind_direction_deg: Optional[float] = Field(310.0, description="Wind direction in degrees")


# --- Health Response ---
class HealthResponse(BaseModel):
    status: str = "healthy"
    service: str = "VaayuNetra Environmental Intelligence BFF"
    version: str = "1.0.0"
    timestamp: str
    endpoints: Dict[str, str]
    active_incidents_count: int


# --- Environmental Event (SIH / Docs Spec) ---
class EnvironmentalEvent(BaseModel):
    event_id: str
    created_at: str
    geometry: GeoJSONGeometry
    severity: str
    confidence: float
    priority: int
    pollutants: List[Dict[str, Any]] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    source_hypotheses: List[Dict[str, Any]] = Field(default_factory=list)
    forecasts: List[Dict[str, Any]] = Field(default_factory=list)
    exposure: Dict[str, Any] = Field(default_factory=dict)
    jurisdiction: Dict[str, Any] = Field(default_factory=dict)
    recommended_actions: List[str] = Field(default_factory=list)
    status: str = "ACTIVE"


# --- Enriched Event Item (Authority Web Dashboard) ---
class EnrichedEventItem(BaseModel):
    id: str
    event_id: Optional[str] = None
    title: str
    status: str  # ACTIVE, CORROBORATED, CANDIDATE, RESOLVED
    severity: str  # critical, high, moderate, low
    confidence: float
    pollutant: str = "PM2.5"
    peakValue: float
    unit: str = "µg/m³"
    baseline: float
    anomalyScore: float
    lat: float
    lng: float
    detectedAt: str
    sourceHypotheses: List[Dict[str, Any]] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    forecast: List[Dict[str, Any]] = Field(default_factory=list)
    exposure: Dict[str, Any] = Field(default_factory=dict)
    priority: int
    city: Optional[str] = "Delhi NCR"
    jurisdiction: str
    recommendedAction: str
    timeline: List[Dict[str, Any]] = Field(default_factory=list)


# --- Region & Multi-Region Forecast Models ---
class RegionInfo(BaseModel):
    name: str
    state: str
    lat: float
    lng: float
    current_aqi: int
    status: str
    dominant_pollutant: str = "PM2.5"
    weather_desc: str = "NW 3.6 m/s · 28°C"
    # Live pollutant concentration snapshot (µg/m³ equivalents) driving dashboard metric bubbles
    metrics: Dict[str, float] = Field(default_factory=dict)


class HourlyForecastPoint(BaseModel):
    t: str
    aqi: int


class HourlyForecastResponse(BaseModel):
    city: str = "Delhi NCR"
    state: str = "Delhi"
    country: str = "India"
    lat: float = 28.6139
    lng: float = 77.2090
    current_aqi: int = 186
    category: str = "Poor"
    dominant_pollutant: str = "PM2.5"
    hourly: List[HourlyForecastPoint] = Field(default_factory=list)


# --- Authority Action Models ---
class ActionItem(BaseModel):
    id: str
    eventId: str
    type: str  # FIELD_INSPECTION, NOTICE_DRAFT, DUST_SUPPRESSION, FIRE_SERVICE_ALERT, PUBLIC_ADVISORY
    assignee: str
    status: str = "DISPATCHED"  # DISPATCHED, IN_PROGRESS, PENDING, COMPLETED
    createdAt: str
    eta: Optional[str] = None
    notes: Optional[str] = None


class ActionCreateRequest(BaseModel):
    eventId: str
    type: Optional[str] = "FIELD_INSPECTION"
    assignee: Optional[str] = "SDM South-East"
    notes: Optional[str] = None


# --- Public Advisory Models ---
class AdvisoryItem(BaseModel):
    id: str
    eventId: str
    title: str
    audience: str
    languages: List[str] = Field(default_factory=lambda: ["EN", "HI"])
    channels: List[str] = Field(default_factory=lambda: ["SMS", "IVR", "App"])
    status: str = "SENT"  # DRAFT, SENT
    sentAt: Optional[str] = None
    message: Optional[str] = None


class AdvisoryCreateRequest(BaseModel):
    eventId: str
    title: Optional[str] = None
    audience: Optional[str] = "Residents within 2 km of event"
    languages: List[str] = Field(default_factory=lambda: ["EN", "HI"])
    channels: List[str] = Field(default_factory=lambda: ["SMS", "IVR", "App"])
    message: Optional[str] = "Air quality in your area is currently poor due to a local pollution event. Sensitive groups should limit outdoor activity."


# --- Legal Notice Dossier Document ---
class LegalNoticeDocument(BaseModel):
    notice_id: str
    event_id: str
    reference_no: str
    issuing_authority: str
    recipient: str
    issued_at: str
    subject: str
    event_title: str
    severity: str
    coordinates: str
    peak_pollutant: str
    baseline: str
    anomaly: str
    evidence_summary: List[Dict[str, str]] = Field(default_factory=list)
    impact_summary: Dict[str, Any] = Field(default_factory=dict)
    directives: List[str] = Field(default_factory=list)
    compliance_deadline_hours: int = 24
    penal_provisions: str
    html_document: str
    hindi_document: Optional[str] = None
    gemini_reasoning: Optional[str] = None
    statutory_citation: Optional[str] = "Section 31A, Air (Prevention and Control of Pollution) Act, 1981"


# --- Alert Item (docs/api.md) ---
class AlertItem(BaseModel):
    id: str
    event_id: str
    title: str
    severity: str
    message: str
    created_at: str
    acknowledged: bool = False
    authority: str


# --- Sensor Data Input (docs/api.md) ---
class SensorDataInput(BaseModel):
    sensor_id: str
    timestamp: str
    latitude: float
    longitude: float
    parameter: str = "pm25"
    value: float
    unit: str = "ug/m3"
    quality_flag: str = "good"


# --- Sub-resource Responses (docs/api.md) ---
class EventEvidenceResponse(BaseModel):
    event_id: str
    evidence: List[Dict[str, Any]] = Field(default_factory=list)


class EventForecastResponse(BaseModel):
    event_id: str
    forecast: List[Dict[str, Any]] = Field(default_factory=list)


class EventRiskResponse(BaseModel):
    event_id: str
    priority: int
    exposure: Dict[str, Any] = Field(default_factory=dict)


