"""Unified, mobile-ready Pydantic v2 response contracts for VaayuNetra Flutter client."""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class AtmosphericSummary(BaseModel):
    """Regional and local atmospheric column metrics."""
    model_config = ConfigDict(extra="ignore")

    wind_speed_kmh: float = Field(..., description="Surface wind speed in km/h")
    wind_direction_deg: float = Field(..., description="Surface wind direction in degrees (origin)")
    temperature_c: float = Field(..., description="Ambient temperature in degrees Celsius")
    regional_no2_ugm3: float = Field(..., description="Regional tropospheric nitrogen dioxide in µg/m³")
    aerosol_optical_depth: float = Field(..., description="Total vertical aerosol optical depth column at 550nm")


class VerificationSummary(BaseModel):
    """Multi-tier optical and satellite verification summary."""
    model_config = ConfigDict(extra="ignore")

    vision_verified: bool = Field(..., description="Whether photographic evidence verified smoke/fire")
    vision_confidence: float = Field(..., description="Confidence score of vision model (0.0 - 1.0)")
    satellite_thermal_match: bool = Field(..., description="Whether NASA FIRMS detected thermal hotspot")
    thermal_distance_m: float = Field(..., description="Distance in meters from coordinate to satellite thermal anomaly")


class ImpactAssessment(BaseModel):
    """Downwind community vulnerability and receptor impact assessment."""
    model_config = ConfigDict(extra="ignore")

    vulnerability_score: int = Field(..., description="Composite community vulnerability score (0 - 100)")
    alert_priority: Literal["LOW", "MODERATE", "HIGH", "CRITICAL"] = Field(
        ..., description="Standardized alert severity level"
    )
    impacted_receptors: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of impacted facilities with name, amenity_type, distance_m",
    )


class IncidentTicketResponse(BaseModel):
    """Unified incident ticket contract merged across all 5 modular sockets."""
    model_config = ConfigDict(extra="ignore")

    ticket_id: str = Field(..., description="Unique sequential incident identifier (e.g. VN-101)")
    timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    category: str = Field(..., description="Incident category classification")
    latitude: float = Field(..., description="Incident source latitude")
    longitude: float = Field(..., description="Incident source longitude")
    verification: VerificationSummary = Field(..., description="Combined vision and satellite verification")
    atmospheric: AtmosphericSummary = Field(..., description="Combined local wind vector and CAMS column")
    impact: ImpactAssessment = Field(..., description="Community receptor vulnerability analysis")
    plume_geojson: Dict[str, Any] = Field(..., description="GeoJSON Feature containing dispersion cone polygon")


class PlumeWarning(BaseModel):
    """Warning payload delivered when coordinates intersect an active plume."""
    model_config = ConfigDict(extra="ignore")

    incident_id: str
    category: str
    origin_lat: float
    origin_lon: float
    wind_speed_kmh: float
    heading_deg: float
    vulnerability_score: int
    advisory: str


class FeedResponse(BaseModel):
    """Citizen ambient feed and active plume warning contract."""
    model_config = ConfigDict(extra="allow")

    latitude: float
    longitude: float
    inside_active_plume: bool
    active_warnings: List[Dict[str, Any]]
    street_pm2_5: float
    ground_sensors: List[Dict[str, Any]]
    active_incidents: List[IncidentTicketResponse]
    status: Optional[str] = "online"
    location: Optional[str] = None
    aqi: Optional[int] = None
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    hazard_level: Optional[str] = None
    weather: Optional[Dict[str, Any]] = None
    nearby_nodes: Optional[List[Dict[str, Any]]] = None


class HealthResponse(BaseModel):
    """System health and plug-and-socket operational status."""
    status: str
    service: str
    version: str
    sockets: Dict[str, str]
    total_active_incidents: int
