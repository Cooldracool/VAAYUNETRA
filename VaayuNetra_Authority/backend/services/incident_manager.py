import asyncio
from datetime import datetime, timezone
import uuid
from typing import Any, Dict, List, Optional

from backend.models.schemas import (
    ActionCreateRequest,
    ActionItem,
    ActiveWarning,
    AdvisoryCreateRequest,
    AdvisoryItem,
    AIVisionResult,
    AlertItem,
    EnrichedEventItem,
    GeoJSONFeature,
    GeoJSONFeatureCollection,
    GeoJSONGeometry,
    HourlyForecastPoint,
    HourlyForecastResponse,
    ImpactedReceptor,
    IncidentTicketResponse,
    LegalNoticeDocument,
    RegionInfo,
    SatelliteThermalMatch,
    SensorDataInput,
    WindVector,
)
from backend.services.dispersion import (
    calculate_distance_meters,
    calculate_downwind_plume,
    get_bearing_cardinal,
    is_point_inside_plume,
)
from backend.services.receptors import find_impacted_receptors
from backend.services.satellite import find_satellite_thermal_match
from backend.services.weather import get_wind_vector
from backend.services.gemini_service import (
    generate_bilingual_statutory_text,
    generate_multilingual_citizen_advisory,
)


class IncidentManager:
    def __init__(self):
        self.incidents: Dict[str, IncidentTicketResponse] = {}
        self.enriched_events: Dict[str, EnrichedEventItem] = {}
        self.actions: Dict[str, ActionItem] = {}
        self.advisories: Dict[str, AdvisoryItem] = {}
        self.alerts: List[AlertItem] = []
        self.sensor_readings: List[SensorDataInput] = []
        self.hourly_forecast: List[HourlyForecastPoint] = []
        self._init_seed_incidents()
        self._init_seed_frontend_data()
        
    def _init_seed_incidents(self):
        """Pre-seeds realistic verified incidents in Delhi NCR on startup."""
        now_iso = datetime.now(timezone.utc).isoformat()
        
        # 1. Ghazipur Landfill Fire Incident
        tkt_1 = "TKT-20260906-8801"
        lat1, lon1 = 28.6280, 77.3290
        wind1 = WindVector(speed_mps=4.2, direction_deg=295.0, cardinal="WNW", source="Open-Meteo High-Resolution")
        plume1_dict = calculate_downwind_plume(lat1, lon1, wind1.speed_mps, wind1.direction_deg, "CRITICAL", 4.2)
        plume1 = GeoJSONGeometry(type="Polygon", coordinates=plume1_dict["coordinates"])
        receptors1 = find_impacted_receptors(plume1_dict, lat1, lon1, wind1.speed_mps)
        
        self.incidents[tkt_1] = IncidentTicketResponse(
            ticket_id=tkt_1,
            created_at=now_iso,
            status="VERIFIED",
            category="waste_burning",
            latitude=lat1,
            longitude=lon1,
            ai_vision=AIVisionResult(
                confidence=0.95,
                detected_category="OPEN_BURNING",
                visual_evidence=True,
                model_version="Google-Gemini-1.5-Flash",
                details="Open combustion flare and high particulate density smoke column identified.",
                reasoning="Dense pyrocumulus column with low base chrominance variance and active combustion thermal flare.",
                plume_density="Ringelmann 4 (80% opacity)",
                ai_engine="Google Gemini Multimodal",
                recommended_authority="MCD Solid Waste Flying Squad",
            ),
            satellite_thermal_match=SatelliteThermalMatch(
                matched=True,
                confidence=0.94,
                satellite_source="NASA FIRMS VIIRS (S-NPP)",
                brightness_temp_k=341.2,
                frp_mw=24.8,
                distance_km=0.15,
                detected_at=now_iso,
            ),
            wind_vector=wind1,
            plume_geometry=plume1,
            impacted_receptors=receptors1,
            severity="CRITICAL",
            priority_score=94,
            recommended_action="Dispatch MCD Flying Squad Unit 4 and East Delhi Fire Tender; notify sensitive receptors.",
            assigned_authority="Municipal Corporation of Delhi (MCD) - Solid Waste Management",
        )
        
        # 2. Bawana Industrial Emission Anomaly
        tkt_2 = "TKT-20260906-8802"
        lat2, lon2 = 28.7950, 77.0420
        wind2 = WindVector(speed_mps=3.6, direction_deg=315.0, cardinal="NW", source="Open-Meteo High-Resolution")
        plume2_dict = calculate_downwind_plume(lat2, lon2, wind2.speed_mps, wind2.direction_deg, "HIGH", 3.2)
        plume2 = GeoJSONGeometry(type="Polygon", coordinates=plume2_dict["coordinates"])
        receptors2 = find_impacted_receptors(plume2_dict, lat2, lon2, wind2.speed_mps)
        
        self.incidents[tkt_2] = IncidentTicketResponse(
            ticket_id=tkt_2,
            created_at=now_iso,
            status="ACTIVE",
            category="industrial_emission",
            latitude=lat2,
            longitude=lon2,
            ai_vision=AIVisionResult(
                confidence=0.88,
                detected_category="INDUSTRIAL_EMISSION",
                visual_evidence=True,
                model_version="Google-Gemini-1.5-Flash",
                details="High-volume black smoke plume from unauthorized industrial smelting stack.",
                reasoning="Continuous point-source stack plume exceeding standard opacity baselines with visible particulate fallout.",
                plume_density="Ringelmann 3 (60% opacity)",
                ai_engine="Google Gemini Multimodal",
                recommended_authority="DPCC Industrial Enforcement Wing",
            ),
            satellite_thermal_match=SatelliteThermalMatch(
                matched=True,
                confidence=0.82,
                satellite_source="NASA FIRMS MODIS (Terra)",
                brightness_temp_k=329.8,
                frp_mw=14.1,
                distance_km=0.42,
                detected_at=now_iso,
            ),
            wind_vector=wind2,
            plume_geometry=plume2,
            impacted_receptors=receptors2,
            severity="HIGH",
            priority_score=82,
            recommended_action="Issue immediate show-cause notice and dispatch DPCC Industrial Enforcement team.",
            assigned_authority="Delhi Pollution Control Committee (DPCC) - Industrial Enforcement",
        )
        
        # 3. Anand Vihar Transit Construction Dust & Biomass
        tkt_3 = "TKT-20260906-8803"
        lat3, lon3 = 28.6476, 77.3158
        wind3 = WindVector(speed_mps=3.1, direction_deg=285.0, cardinal="WNW", source="Open-Meteo High-Resolution")
        plume3_dict = calculate_downwind_plume(lat3, lon3, wind3.speed_mps, wind3.direction_deg, "MODERATE", 2.4)
        plume3 = GeoJSONGeometry(type="Polygon", coordinates=plume3_dict["coordinates"])
        receptors3 = find_impacted_receptors(plume3_dict, lat3, lon3, wind3.speed_mps)
        
        self.incidents[tkt_3] = IncidentTicketResponse(
            ticket_id=tkt_3,
            created_at=now_iso,
            status="DISPATCHED",
            category="construction_dust",
            latitude=lat3,
            longitude=lon3,
            ai_vision=AIVisionResult(
                confidence=0.86,
                detected_category="DUST",
                visual_evidence=True,
                model_version="Google-Gemini-1.5-Flash",
                details="Fugitive dust plume from unpaved road shoulder and transit construction.",
                reasoning="Ground-level sandy particulate suspension with high opacity along transit road shoulder.",
                plume_density="Ringelmann 2 (40% opacity)",
                ai_engine="Google Gemini Multimodal",
                recommended_authority="PWD Anti-Smog Dust Mitigation",
            ),
            satellite_thermal_match=SatelliteThermalMatch(
                matched=False,
                confidence=None,
                satellite_source="NASA FIRMS (VIIRS/MODIS)",
                brightness_temp_k=None,
                frp_mw=None,
                distance_km=None,
                detected_at=None,
            ),
            wind_vector=wind3,
            plume_geometry=plume3,
            impacted_receptors=receptors3,
            severity="MODERATE",
            priority_score=68,
            recommended_action="Deploy PWD Anti-Smog Gun and mechanical street sweepers across ISBT corridor.",
            assigned_authority="Public Works Department (PWD) - Dust Mitigation Wing",
        )

    def get_all_incidents(self) -> List[IncidentTicketResponse]:
        return list(self.incidents.values())

    def get_incident(self, ticket_id: str) -> Optional[IncidentTicketResponse]:
        return self.incidents.get(ticket_id)

    async def create_incident_ticket(
        self,
        latitude: float,
        longitude: float,
        category: str,
        ai_vision: AIVisionResult,
        custom_wind_speed: Optional[float] = None,
        custom_wind_deg: Optional[float] = None,
        custom_severity: Optional[str] = None,
    ) -> IncidentTicketResponse:
        """Creates and stores a verified incident ticket with all correlated evidence."""
        ticket_id = f"TKT-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
        now_iso = datetime.now(timezone.utc).isoformat()
        
        # 1. Fetch wind vector
        if custom_wind_speed is not None and custom_wind_deg is not None:
            cardinal = get_bearing_cardinal(latitude, longitude, latitude + 0.01, longitude + 0.01)
            wind_vector = WindVector(
                speed_mps=custom_wind_speed,
                direction_deg=custom_wind_deg,
                cardinal=cardinal,
                source="Simulated / High-Res Model",
            )
        else:
            wind_vector = await get_wind_vector(latitude, longitude)
            
        # 2. Correlate Satellite Thermal Match
        thermal_match = find_satellite_thermal_match(latitude, longitude, category)
        
        # 3. Severity & Priority determination
        severity = custom_severity or ("CRITICAL" if thermal_match.matched and thermal_match.frp_mw and thermal_match.frp_mw > 20.0 else "HIGH")
        priority = 88 if severity == "CRITICAL" else (78 if severity == "HIGH" else 60)
        if thermal_match.matched:
            priority = min(98, priority + 8)
            
        # 4. Calculate Plume Geometry
        plume_dict = calculate_downwind_plume(
            origin_lat=latitude,
            origin_lon=longitude,
            wind_speed_mps=wind_vector.speed_mps,
            wind_direction_deg=wind_vector.direction_deg,
            severity=severity,
        )
        plume_geom = GeoJSONGeometry(type="Polygon", coordinates=plume_dict["coordinates"])
        
        # 5. Discover impacted sensitive receptors
        impacted_receptors = find_impacted_receptors(
            plume_geojson=plume_dict,
            origin_lat=latitude,
            origin_lon=longitude,
            wind_speed_mps=wind_vector.speed_mps,
        )
        
        # 6. Action and Authority
        cat_lower = category.lower()
        if "burn" in cat_lower or "fire" in cat_lower or "stubble" in cat_lower:
            assigned_authority = "Municipal Corporation of Delhi (MCD) - Solid Waste Flying Squad"
            rec_action = f"Dispatch municipal flying squad to douse burning at ({latitude:.4f}, {longitude:.4f}). Warn nearby institutions."
        elif "industrial" in cat_lower:
            assigned_authority = "Delhi Pollution Control Committee (DPCC) - Industrial Enforcement Cell"
            rec_action = f"Issue cease-and-desist inspection order for stack emissions at ({latitude:.4f}, {longitude:.4f})."
        else:
            assigned_authority = "Public Works Department (PWD) / Traffic Police Rapid Action"
            rec_action = f"Deploy local dust suppression and traffic diversion around ({latitude:.4f}, {longitude:.4f})."
            
        ticket = IncidentTicketResponse(
            ticket_id=ticket_id,
            created_at=now_iso,
            status="VERIFIED",
            category=category,
            latitude=latitude,
            longitude=longitude,
            ai_vision=ai_vision,
            satellite_thermal_match=thermal_match,
            wind_vector=wind_vector,
            plume_geometry=plume_geom,
            impacted_receptors=impacted_receptors,
            severity=severity,
            priority_score=priority,
            recommended_action=rec_action,
            assigned_authority=assigned_authority,
        )
        
        self.incidents[ticket_id] = ticket
        self._add_enriched_from_incident(ticket)
        return ticket

    def check_active_warnings(self, user_lat: float, user_lon: float) -> List[ActiveWarning]:
        """
        Flags if user is inside any active smoke plume and computes distance and direction.
        """
        warnings: List[ActiveWarning] = []
        for inc in self.incidents.values():
            plume_dict = {"type": inc.plume_geometry.type, "coordinates": inc.plume_geometry.coordinates}
            inside = is_point_inside_plume(user_lat, user_lon, plume_dict)
            dist_m = calculate_distance_meters(user_lat, user_lon, inc.latitude, inc.longitude)
            
            # If user is inside the plume or within 350 meters
            if inside or dist_m < 350.0:
                direction = get_bearing_cardinal(inc.latitude, inc.longitude, user_lat, user_lon)
                dist_km = max(0.1, dist_m / 1000.0)
                eta_min = max(2, int(dist_m / (inc.wind_vector.speed_mps * 60))) if inc.wind_vector.speed_mps > 0 else 15
                
                hi_msg = generate_multilingual_citizen_advisory(
                    pollutant="PM2.5", peak_value=312.0, unit="µg/m³",
                    distance_km=dist_km, eta_minutes=eta_min, lang="HI"
                )
                pa_msg = generate_multilingual_citizen_advisory(
                    pollutant="PM2.5", peak_value=312.0, unit="µg/m³",
                    distance_km=dist_km, eta_minutes=eta_min, lang="PA"
                )
                
                warnings.append(
                    ActiveWarning(
                        incident_id=inc.ticket_id,
                        category=inc.category,
                        severity=inc.severity,
                        inside_plume=inside,
                        distance_meters=dist_m,
                        direction_from_user=direction,
                        message=(
                            f"⚠️ Smoke Plume Alert: You are inside the dispersion path of a {inc.severity} "
                            f"{inc.category.replace('_', ' ')} incident located {int(dist_m)}m away. "
                            f"Recommended to stay indoors and close windows."
                        ),
                        hindi_message=hi_msg,
                        punjabi_message=pa_msg,
                    )
                )
        return warnings

    def get_municipal_geojson(self) -> GeoJSONFeatureCollection:
        """
        Returns a standard GeoJSON FeatureCollection containing all verified incident points
        and their projected downwind plume dispersion polygons ready to render on a map.
        """
        features: List[GeoJSONFeature] = []
        
        for inc in self.incidents.values():
            # 1. Incident Point Feature
            point_feature = GeoJSONFeature(
                type="Feature",
                geometry=GeoJSONGeometry(
                    type="Point",
                    coordinates=[inc.longitude, inc.latitude],
                ),
                properties={
                    "id": inc.ticket_id,
                    "feature_type": "incident_point",
                    "category": inc.category,
                    "severity": inc.severity,
                    "priority": inc.priority_score,
                    "status": inc.status,
                    "ai_confidence": inc.ai_vision.confidence,
                    "ai_category": inc.ai_vision.detected_category,
                    "thermal_match": inc.satellite_thermal_match.matched,
                    "satellite_source": inc.satellite_thermal_match.satellite_source,
                    "wind_speed": inc.wind_vector.speed_mps,
                    "wind_direction": inc.wind_vector.direction_deg,
                    "receptors_impacted": len(inc.impacted_receptors),
                    "impacted_receptors": [r.model_dump() for r in inc.impacted_receptors],
                    "recommended_action": inc.recommended_action,
                    "assigned_authority": inc.assigned_authority,
                    "created_at": inc.created_at,
                    "summary": f"{inc.severity} {inc.category.replace('_', ' ').title()} - Priority {inc.priority_score}",
                },
            )
            features.append(point_feature)
            
            # 2. Projected Downwind Plume Polygon Feature
            severity_colors = {
                "CRITICAL": "#dc2626",  # Red
                "HIGH": "#ea580c",      # Orange
                "MODERATE": "#eab308",  # Amber/Yellow
                "LOW": "#10b981",       # Green
            }
            color = severity_colors.get(inc.severity.upper(), "#ef4444")
            
            plume_feature = GeoJSONFeature(
                type="Feature",
                geometry=inc.plume_geometry,
                properties={
                    "id": f"PLUME-{inc.ticket_id}",
                    "feature_type": "plume_polygon",
                    "incident_id": inc.ticket_id,
                    "category": inc.category,
                    "severity": inc.severity,
                    "color": color,
                    "fill_opacity": 0.35,
                    "wind_direction_deg": inc.wind_vector.direction_deg,
                    "wind_speed_mps": inc.wind_vector.speed_mps,
                    "forecast_horizon_hours": 3,
                    "receptors_count": len(inc.impacted_receptors),
                },
            )
            features.append(plume_feature)
            
        return GeoJSONFeatureCollection(type="FeatureCollection", features=features)

    def _init_seed_frontend_data(self):
        """Pre-seeds rich environmental events, hourly forecasts, actions, and advisories for dashboard."""
        # 1. Seed Rich Events (from User Specification)
        seed_events = [
            EnrichedEventItem(
                id="EVT-2026-0847",
                title="Open burning cluster — Okhla landfill perimeter",
                status="ACTIVE",
                severity="critical",
                confidence=0.87,
                pollutant="PM2.5",
                peakValue=312.0,
                unit="µg/m³",
                baseline=68.0,
                anomalyScore=4.6,
                lat=28.5355,
                lng=77.2910,
                detectedAt="2026-09-05T18:42:00+05:30",
                sourceHypotheses=[
                    {"category": "OPEN_BURNING", "prob": 0.62},
                    {"category": "INDUSTRIAL_EMISSION", "prob": 0.18},
                    {"category": "UNKNOWN", "prob": 0.12},
                    {"category": "CONSTRUCTION_DUST", "prob": 0.08},
                ],
                evidence=[
                    {"type": "sensor", "label": "CAAQMS Okhla Phase-2", "detail": "PM2.5 298→312 µg/m³ in 45 min", "time": "18:42"},
                    {"type": "citizen", "label": "Citizen report #CR-2291", "detail": "Visible smoke + burning smell, geotagged photo", "time": "18:28"},
                    {"type": "cv", "label": "CV validation", "detail": "Smoke plume detected (confidence 0.91)", "time": "18:31"},
                    {"type": "weather", "label": "Wind context", "detail": "NE 6 km/h, low mixing height", "time": "18:00"},
                ],
                forecast=[
                    {"hour": 1, "pm25": 285}, {"hour": 2, "pm25": 240}, {"hour": 3, "pm25": 198},
                    {"hour": 4, "pm25": 165}, {"hour": 5, "pm25": 142}, {"hour": 6, "pm25": 125},
                ],
                exposure={"population": 48200, "schools": 6, "hospitals": 2, "corridors": ["Mathura Road freight"]},
                priority=94,
                jurisdiction="SDM South-East Delhi + DPCC",
                recommendedAction="Immediate field inspection + fire service alert. Issue notice to landfill operator. Activate local public advisory for 2 km radius.",
                timeline=[
                    {"time": "17:30", "text": "First anomalous reading at Okhla CAAQMS"},
                    {"time": "18:05", "text": "Local baseline exceeded (z > 3.5)"},
                    {"time": "18:28", "text": "Citizen report received with image"},
                    {"time": "18:31", "text": "CV confirmed smoke plume"},
                    {"time": "18:42", "text": "Event created → escalated to ACTIVE"},
                    {"time": "18:55", "text": "Priority 94 — routed to SDM + DPCC"},
                ],
            ),
            EnrichedEventItem(
                id="EVT-2026-0841",
                title="Construction dust plume — Outer Ring Road, Sarita Vihar",
                status="ACTIVE",
                severity="high",
                confidence=0.74,
                pollutant="PM10",
                peakValue=428.0,
                unit="µg/m³",
                baseline=145.0,
                anomalyScore=2.9,
                lat=28.5340,
                lng=77.2700,
                detectedAt="2026-09-05T16:15:00+05:30",
                sourceHypotheses=[
                    {"category": "CONSTRUCTION_DUST", "prob": 0.71},
                    {"category": "ROAD_TRAFFIC", "prob": 0.19},
                    {"category": "UNKNOWN", "prob": 0.10},
                ],
                evidence=[
                    {"type": "sensor", "label": "IoT node ORR-SV-03", "detail": "PM10 sustained >350 for 90 min", "time": "16:15"},
                    {"type": "citizen", "label": "Citizen report #CR-2284", "detail": "Uncovered debris & earthwork", "time": "15:50"},
                ],
                forecast=[
                    {"hour": 1, "pm25": 110}, {"hour": 2, "pm25": 95}, {"hour": 3, "pm25": 82},
                ],
                exposure={"population": 21500, "schools": 3, "hospitals": 0, "corridors": ["Outer Ring Road"]},
                priority=71,
                jurisdiction="MCD South + Traffic Police",
                recommendedAction="Issue stop-work / dust-suppression notice. Request water sprinkling on ORR stretch.",
                timeline=[
                    {"time": "15:20", "text": "IoT sensors show rising PM10"},
                    {"time": "15:50", "text": "Citizen geotagged construction site"},
                    {"time": "16:15", "text": "Event confirmed ACTIVE"},
                ],
            ),
            EnrichedEventItem(
                id="EVT-2026-0839",
                title="Traffic corridor spike — ITO to Rajghat",
                status="CORROBORATED",
                severity="moderate",
                confidence=0.68,
                pollutant="NO2",
                peakValue=89.0,
                unit="ppb",
                baseline=42.0,
                anomalyScore=2.1,
                lat=28.6280,
                lng=77.2410,
                detectedAt="2026-09-05T14:40:00+05:30",
                sourceHypotheses=[
                    {"category": "ROAD_TRAFFIC", "prob": 0.78},
                    {"category": "UNKNOWN", "prob": 0.22},
                ],
                evidence=[
                    {"type": "sensor", "label": "CAAQMS ITO", "detail": "NO2 elevated during peak hour", "time": "14:40"},
                    {"type": "weather", "label": "Calm winds", "detail": "Wind < 3 km/h, inversion layer", "time": "14:00"},
                ],
                forecast=[
                    {"hour": 1, "pm25": 72}, {"hour": 2, "pm25": 58},
                ],
                exposure={"population": 34000, "schools": 2, "hospitals": 1, "corridors": ["Ring Road", "ITO"]},
                priority=58,
                jurisdiction="Traffic Police + DPCC",
                recommendedAction="Monitor. Consider temporary traffic diversion if persists beyond 2 h.",
                timeline=[
                    {"time": "14:10", "text": "Peak-hour NO2 rise detected"},
                    {"time": "14:40", "text": "Corroborated with wind context"},
                ],
            ),
            EnrichedEventItem(
                id="EVT-2026-0822",
                title="Agricultural residue burning — fringe NCR (Haryana border)",
                status="RESOLVED",
                severity="high",
                confidence=0.81,
                pollutant="PM2.5",
                peakValue=265.0,
                unit="µg/m³",
                baseline=55.0,
                anomalyScore=3.8,
                lat=28.7200,
                lng=76.9800,
                detectedAt="2026-09-04T21:10:00+05:30",
                sourceHypotheses=[
                    {"category": "AGRICULTURAL_BURNING", "prob": 0.69},
                    {"category": "OPEN_BURNING", "prob": 0.21},
                    {"category": "UNKNOWN", "prob": 0.10},
                ],
                evidence=[
                    {"type": "firms", "label": "FIRMS thermal anomaly", "detail": "Hotspot cluster within 8 km", "time": "20:55"},
                    {"type": "sensor", "label": "CAAQMS Bawana", "detail": "PM2.5 surge overnight", "time": "21:10"},
                ],
                forecast=[],
                exposure={"population": 19000, "schools": 1, "hospitals": 0, "corridors": []},
                priority=0,
                jurisdiction="Haryana PCB + Delhi DPCC",
                recommendedAction="Closed — residual monitoring for 12 h.",
                timeline=[
                    {"time": "20:55", "text": "FIRMS hotspot detected"},
                    {"time": "21:10", "text": "Ground sensors confirmed"},
                    {"time": "09:00", "text": "Levels returned to baseline — RESOLVED"},
                ],
            ),
            EnrichedEventItem(
                id="EVT-2026-0849",
                title="Candidate: Industrial stack anomaly — Mayapuri",
                status="CANDIDATE",
                severity="moderate",
                confidence=0.52,
                pollutant="SO2",
                peakValue=48.0,
                unit="ppb",
                baseline=12.0,
                anomalyScore=2.4,
                lat=28.6300,
                lng=77.1200,
                detectedAt="2026-09-05T19:05:00+05:30",
                sourceHypotheses=[
                    {"category": "INDUSTRIAL_EMISSION", "prob": 0.55},
                    {"category": "UNKNOWN", "prob": 0.45},
                ],
                evidence=[
                    {"type": "sensor", "label": "IoT Mayapuri-01", "detail": "SO2 elevated, single sensor", "time": "19:05"},
                ],
                forecast=[],
                exposure={"population": 12000, "schools": 1, "hospitals": 0, "corridors": []},
                priority=41,
                jurisdiction="DPCC Industrial",
                recommendedAction="Await corroboration from second sensor or citizen evidence before escalation.",
                timeline=[
                    {"time": "19:05", "text": "Single-sensor anomaly flagged as CANDIDATE"},
                ],
            ),
            EnrichedEventItem(
                id="EVT-2026-0901",
                title="Landfill combustion flare — Deonar sector",
                city="Mumbai",
                status="ACTIVE",
                severity="critical",
                confidence=0.92,
                pollutant="PM2.5",
                peakValue=288.0,
                unit="µg/m³",
                baseline=45.0,
                anomalyScore=4.1,
                lat=19.0550,
                lng=72.9300,
                detectedAt="2026-09-06T01:20:00+05:30",
                sourceHypotheses=[
                    {"category": "OPEN_BURNING", "prob": 0.75},
                    {"category": "INDUSTRIAL_EMISSION", "prob": 0.25},
                ],
                evidence=[
                    {"type": "firms", "label": "NASA FIRMS VIIRS Hotspot", "detail": "FRP 18.5 MW detected at Deonar ridge", "time": "01:15"},
                    {"type": "sensor", "label": "Chembur East CAAQMS", "detail": "PM2.5 reached 288 µg/m³", "time": "01:20"},
                ],
                forecast=[
                    {"hour": 1, "pm25": 260}, {"hour": 2, "pm25": 210}, {"hour": 3, "pm25": 175},
                ],
                exposure={"population": 54000, "schools": 7, "hospitals": 3, "corridors": ["Eastern Freeway"]},
                priority=91,
                jurisdiction="BMC Solid Waste & MPCB",
                recommendedAction="Dispatch Chembur Fire Squad and deploy mist cannons along Mankhurd corridor.",
                timeline=[
                    {"time": "01:15", "text": "Satellite thermal match confirmed"},
                    {"time": "01:20", "text": "Event marked CRITICAL"},
                ],
            ),
            EnrichedEventItem(
                id="EVT-2026-0902",
                title="Solid waste burning — Dhapa dumpsite",
                city="Kolkata",
                status="ACTIVE",
                severity="high",
                confidence=0.84,
                pollutant="PM2.5",
                peakValue=245.0,
                unit="µg/m³",
                baseline=52.0,
                anomalyScore=3.4,
                lat=22.5450,
                lng=88.4200,
                detectedAt="2026-09-06T00:45:00+05:30",
                sourceHypotheses=[
                    {"category": "OPEN_BURNING", "prob": 0.68},
                    {"category": "UNKNOWN", "prob": 0.32},
                ],
                evidence=[
                    {"type": "sensor", "label": "EM Bypass CAAQMS", "detail": "PM2.5 spike >220", "time": "00:45"},
                ],
                forecast=[
                    {"hour": 1, "pm25": 225}, {"hour": 2, "pm25": 185}, {"hour": 3, "pm25": 150},
                ],
                exposure={"population": 38000, "schools": 4, "hospitals": 1, "corridors": ["EM Bypass"]},
                priority=78,
                jurisdiction="KMC Solid Waste & WBPCB",
                recommendedAction="Deploy water dousing tankers to Dhapa southern perimeter.",
                timeline=[
                    {"time": "00:45", "text": "Elevated ground reading at EM Bypass node"},
                ],
            ),
            EnrichedEventItem(
                id="EVT-2026-0903",
                title="Industrial metallurgical stack emissions — Peenya",
                city="Bengaluru",
                status="ACTIVE",
                severity="moderate",
                confidence=0.72,
                pollutant="PM10",
                peakValue=195.0,
                unit="µg/m³",
                baseline=65.0,
                anomalyScore=2.6,
                lat=13.0300,
                lng=77.5100,
                detectedAt="2026-09-05T22:15:00+05:30",
                sourceHypotheses=[
                    {"category": "INDUSTRIAL_EMISSION", "prob": 0.79},
                    {"category": "ROAD_TRAFFIC", "prob": 0.21},
                ],
                evidence=[
                    {"type": "sensor", "label": "Peenya Industrial Node 4", "detail": "PM10 elevated for 3 hours", "time": "22:15"},
                ],
                forecast=[
                    {"hour": 1, "pm25": 95}, {"hour": 2, "pm25": 80},
                ],
                exposure={"population": 26000, "schools": 3, "hospitals": 1, "corridors": ["Tumkur Road"]},
                priority=62,
                jurisdiction="KSPCB Industrial Vigilance",
                recommendedAction="Issue inspection notice to smelting cluster on 4th Phase.",
                timeline=[
                    {"time": "22:15", "text": "IoT anomaly verified"},
                ],
            ),
            EnrichedEventItem(
                id="EVT-2026-0904",
                title="Transport hub congestion & road dust — Transport Nagar",
                city="Lucknow",
                status="ACTIVE",
                severity="high",
                confidence=0.79,
                pollutant="PM2.5",
                peakValue=275.0,
                unit="µg/m³",
                baseline=72.0,
                anomalyScore=3.5,
                lat=26.7900,
                lng=80.8800,
                detectedAt="2026-09-06T02:10:00+05:30",
                sourceHypotheses=[
                    {"category": "ROAD_TRAFFIC", "prob": 0.58},
                    {"category": "CONSTRUCTION_DUST", "prob": 0.42},
                ],
                evidence=[
                    {"type": "sensor", "label": "Sarojini Nagar CAAQMS", "detail": "PM2.5 persistent elevation", "time": "02:10"},
                ],
                forecast=[
                    {"hour": 1, "pm25": 250}, {"hour": 2, "pm25": 220}, {"hour": 3, "pm25": 190},
                ],
                exposure={"population": 31000, "schools": 2, "hospitals": 1, "corridors": ["Kanpur Road Highway"]},
                priority=76,
                jurisdiction="LMC & UPPCB",
                recommendedAction="Operate anti-smog sweepers and divert freight trucks.",
                timeline=[
                    {"time": "02:10", "text": "Freight corridor spike detected"},
                ],
            ),
        ]
        for ev in seed_events:
            self.enriched_events[ev.id] = ev

        # 2. Seed Hourly Forecast
        hourly_raw = [
            ("04:00", 178), ("05:00", 185), ("06:00", 192), ("07:00", 198),
            ("08:00", 205), ("09:00", 210), ("10:00", 202), ("11:00", 195),
            ("12:00", 188), ("13:00", 182), ("14:00", 175), ("15:00", 170),
            ("16:00", 178), ("17:00", 190), ("18:00", 205), ("19:00", 215),
            ("20:00", 220), ("21:00", 212),
        ]
        self.hourly_forecast = [HourlyForecastPoint(t=t, aqi=aqi) for t, aqi in hourly_raw]

        # 3. Seed Actions
        seed_actions = [
            ActionItem(
                id="ACT-112",
                eventId="EVT-2026-0847",
                type="FIELD_INSPECTION",
                assignee="SDM South-East",
                status="DISPATCHED",
                createdAt="2026-09-05T18:58:00+05:30",
                eta="19:40",
            ),
            ActionItem(
                id="ACT-111",
                eventId="EVT-2026-0847",
                type="NOTICE_DRAFT",
                assignee="DPCC Legal",
                status="IN_PROGRESS",
                createdAt="2026-09-05T19:02:00+05:30",
                eta=None,
            ),
            ActionItem(
                id="ACT-109",
                eventId="EVT-2026-0841",
                type="DUST_SUPPRESSION",
                assignee="MCD South",
                status="PENDING",
                createdAt="2026-09-05T16:30:00+05:30",
                eta=None,
            ),
        ]
        for a in seed_actions:
            self.actions[a.id] = a

        # 4. Seed Advisories
        seed_advisories = [
            AdvisoryItem(
                id="ADV-041",
                eventId="EVT-2026-0847",
                title="Public health advisory — Okhla / Sarita Vihar",
                audience="Residents within 2 km",
                languages=["EN", "HI"],
                channels=["SMS", "IVR", "App"],
                status="SENT",
                sentAt="2026-09-05T19:10:00+05:30",
            ),
            AdvisoryItem(
                id="ADV-040",
                eventId="EVT-2026-0841",
                title="Dust advisory — Outer Ring Road",
                audience="Commuters & nearby residents",
                languages=["EN", "HI"],
                channels=[],
                status="DRAFT",
                sentAt=None,
            ),
            AdvisoryItem(
                id="ADV-039",
                eventId="EVT-2026-0839",
                title="Traffic pollution note — ITO corridor",
                audience="Sensitive groups",
                languages=["EN"],
                channels=["App"],
                status="SENT",
                sentAt="2026-09-05T15:20:00+05:30",
            ),
        ]
        for adv in seed_advisories:
            self.advisories[adv.id] = adv

    def _add_enriched_from_incident(self, inc: IncidentTicketResponse):
        """Converts an IncidentTicketResponse into an EnrichedEventItem for the web dashboard."""
        now_time = datetime.now(timezone.utc).strftime("%H:%M")
        now_iso = inc.created_at
        
        category_title = inc.category.replace("_", " ").title()
        sev_lower = inc.severity.lower()
        
        enriched = EnrichedEventItem(
            id=inc.ticket_id,
            title=f"{inc.severity.title()} incident: {category_title} at ({inc.latitude:.3f}, {inc.longitude:.3f})",
            status=inc.status,
            severity=sev_lower,
            confidence=round(inc.ai_vision.confidence, 2),
            pollutant="PM2.5",
            peakValue=round(220.0 + (inc.priority_score * 1.5), 1),
            unit="µg/m³",
            baseline=65.0,
            anomalyScore=round(2.0 + (inc.priority_score / 25.0), 1),
            lat=inc.latitude,
            lng=inc.longitude,
            detectedAt=now_iso,
            sourceHypotheses=[
                {"category": inc.category.upper(), "prob": inc.ai_vision.confidence},
                {"category": "UNKNOWN", "prob": round(max(0.05, 1.0 - inc.ai_vision.confidence), 2)},
            ],
            evidence=[
                {"type": "cv", "label": "AI Vision Inference", "detail": inc.ai_vision.details or "Visual plume match", "time": now_time},
                {
                    "type": "firms" if inc.satellite_thermal_match.matched else "weather",
                    "label": inc.satellite_thermal_match.satellite_source,
                    "detail": f"FRP {inc.satellite_thermal_match.frp_mw} MW" if inc.satellite_thermal_match.matched else "Wind-guided vector alignment",
                    "time": now_time,
                },
            ],
            forecast=[
                {"hour": 1, "pm25": int(220 + inc.priority_score * 1.2)},
                {"hour": 2, "pm25": int(180 + inc.priority_score * 0.9)},
                {"hour": 3, "pm25": int(140 + inc.priority_score * 0.6)},
            ],
            exposure={
                "population": int(15000 + len(inc.impacted_receptors) * 6000),
                "schools": sum(1 for r in inc.impacted_receptors if r.type == "school"),
                "hospitals": sum(1 for r in inc.impacted_receptors if r.type == "hospital"),
                "corridors": ["Radial Transit Ring"],
            },
            priority=inc.priority_score,
            jurisdiction=inc.assigned_authority,
            recommendedAction=inc.recommended_action,
            timeline=[
                {"time": now_time, "text": f"Incident verified with priority {inc.priority_score}"},
                {"time": now_time, "text": f"Impacted {len(inc.impacted_receptors)} sensitive institutions downwind"},
            ],
        )
        self.enriched_events[inc.ticket_id] = enriched

    def get_enriched_events(self) -> List[EnrichedEventItem]:
        return list(self.enriched_events.values())

    def get_enriched_event(self, event_id: str) -> Optional[EnrichedEventItem]:
        return self.enriched_events.get(event_id)

    def get_hourly_forecast(self) -> List[HourlyForecastPoint]:
        return self.hourly_forecast

    def get_actions(self) -> List[ActionItem]:
        return list(self.actions.values())

    def create_action(self, req: ActionCreateRequest) -> ActionItem:
        action_id = f"ACT-{len(self.actions) + 115}"
        now_iso = datetime.now(timezone.utc).isoformat()
        now_time = datetime.now(timezone.utc).strftime("%H:%M")
        
        # Calculate realistic ETA (+35-45 min from now)
        eta_time = f"{datetime.now(timezone.utc).hour:02d}:{(datetime.now(timezone.utc).minute + 35) % 60:02d}"
        
        action = ActionItem(
            id=action_id,
            eventId=req.eventId,
            type=req.type or "FIELD_INSPECTION",
            assignee=req.assignee or "SDM South-East",
            status="DISPATCHED",
            createdAt=now_iso,
            eta=eta_time,
            notes=req.notes,
        )
        self.actions[action_id] = action
        
        # Also update linked event timeline if found
        ev = self.enriched_events.get(req.eventId)
        if ev:
            ev.timeline.append({"time": now_time, "text": f"Action {action_id} ({action.type}) dispatched to {action.assignee}"})
            if ev.status == "CANDIDATE":
                ev.status = "ACTIVE"
                
        return action

    def get_advisories(self) -> List[AdvisoryItem]:
        return list(self.advisories.values())

    def create_advisory(self, req: AdvisoryCreateRequest) -> AdvisoryItem:
        adv_id = f"ADV-0{len(self.advisories) + 42}"
        now_iso = datetime.now(timezone.utc).isoformat()
        
        title = req.title or f"Public health advisory — {req.eventId}"
        advisory = AdvisoryItem(
            id=adv_id,
            eventId=req.eventId,
            title=title,
            audience=req.audience or "Residents within 2 km of event",
            languages=req.languages or ["EN", "HI"],
            channels=req.channels or ["SMS", "IVR", "App"],
            status="SENT",
            sentAt=now_iso,
            message=req.message,
        )
        self.advisories[adv_id] = advisory
        
        # Append to event timeline
        ev = self.enriched_events.get(req.eventId)
        if ev:
            now_time = datetime.now(timezone.utc).strftime("%H:%M")
            ev.timeline.append({"time": now_time, "text": f"Advisory {adv_id} broadcast across {', '.join(advisory.channels)}"})
            
        return advisory

    def send_advisory(self, advisory_id: str) -> Optional[AdvisoryItem]:
        adv = self.advisories.get(advisory_id)
        if adv:
            adv.status = "SENT"
            adv.sentAt = datetime.now(timezone.utc).isoformat()
        return adv

    def get_regions(self) -> List[RegionInfo]:
        """Returns the catalog of 10 supported Indian regions with current conditions and pollutant metrics."""
        return [
            RegionInfo(name="Delhi NCR", state="Delhi", lat=28.6139, lng=77.2090, current_aqi=186, status="Poor", dominant_pollutant="PM2.5", weather_desc="NW 3.8 m/s · 29°C",
                       metrics={"PM2.5": 108.0, "PM10": 245.0, "NO2": 62.0, "O3": 41.0, "SO2": 18.0}),
            RegionInfo(name="Mumbai", state="Maharashtra", lat=19.0760, lng=72.8777, current_aqi=142, status="Moderate", dominant_pollutant="PM2.5", weather_desc="WSW 4.2 m/s · 31°C",
                       metrics={"PM2.5": 82.0, "PM10": 176.0, "NO2": 48.0, "O3": 36.0, "SO2": 15.0}),
            RegionInfo(name="Bengaluru", state="Karnataka", lat=12.9716, lng=77.5946, current_aqi=85, status="Satisfactory", dominant_pollutant="PM10", weather_desc="E 3.1 m/s · 24°C",
                       metrics={"PM2.5": 40.0, "PM10": 88.0, "NO2": 28.0, "O3": 45.0, "SO2": 9.0}),
            RegionInfo(name="Kolkata", state="West Bengal", lat=22.5726, lng=88.3639, current_aqi=168, status="Poor", dominant_pollutant="PM2.5", weather_desc="S 2.8 m/s · 30°C",
                       metrics={"PM2.5": 98.0, "PM10": 208.0, "NO2": 52.0, "O3": 38.0, "SO2": 16.0}),
            RegionInfo(name="Chennai", state="Tamil Nadu", lat=13.0827, lng=80.2707, current_aqi=94, status="Satisfactory", dominant_pollutant="PM10", weather_desc="SE 4.5 m/s · 32°C",
                       metrics={"PM2.5": 46.0, "PM10": 96.0, "NO2": 30.0, "O3": 42.0, "SO2": 11.0}),
            RegionInfo(name="Hyderabad", state="Telangana", lat=17.3850, lng=78.4867, current_aqi=118, status="Moderate", dominant_pollutant="PM2.5", weather_desc="ESE 3.4 m/s · 28°C",
                       metrics={"PM2.5": 62.0, "PM10": 132.0, "NO2": 38.0, "O3": 40.0, "SO2": 12.0}),
            RegionInfo(name="Ahmedabad", state="Gujarat", lat=23.0225, lng=72.5714, current_aqi=172, status="Poor", dominant_pollutant="PM2.5", weather_desc="WNW 3.9 m/s · 33°C",
                       metrics={"PM2.5": 100.0, "PM10": 216.0, "NO2": 50.0, "O3": 37.0, "SO2": 17.0}),
            RegionInfo(name="Pune", state="Maharashtra", lat=18.5204, lng=73.8567, current_aqi=104, status="Moderate", dominant_pollutant="PM10", weather_desc="W 3.2 m/s · 27°C",
                       metrics={"PM2.5": 52.0, "PM10": 110.0, "NO2": 34.0, "O3": 41.0, "SO2": 12.0}),
            RegionInfo(name="Lucknow", state="Uttar Pradesh", lat=26.8467, lng=80.9462, current_aqi=215, status="Very Poor", dominant_pollutant="PM2.5", weather_desc="NE 2.6 m/s · 29°C",
                       metrics={"PM2.5": 140.0, "PM10": 268.0, "NO2": 68.0, "O3": 35.0, "SO2": 21.0}),
            RegionInfo(name="Patna", state="Bihar", lat=25.5941, lng=85.1376, current_aqi=238, status="Very Poor", dominant_pollutant="PM2.5", weather_desc="E 2.1 m/s · 30°C",
                       metrics={"PM2.5": 160.0, "PM10": 300.0, "NO2": 72.0, "O3": 33.0, "SO2": 24.0}),
            RegionInfo(name="Ranchi", state="Jharkhand", lat=23.3441, lng=85.3096, current_aqi=131, status="Moderate", dominant_pollutant="PM2.5", weather_desc="NE 2.9 m/s · 27°C",
                       metrics={"PM2.5": 74.0, "PM10": 148.0, "NO2": 41.0, "O3": 36.0, "SO2": 14.0}),
        ]

    def get_regional_forecast(self, city_or_region: str = "Delhi NCR") -> HourlyForecastResponse:
        """Computes calibrated 24h hourly forecast trajectory for any Indian region."""
        regions = self.get_regions()
        target = next((r for r in regions if city_or_region.lower() in r.name.lower() or r.name.lower() in city_or_region.lower()), None)
        if not target:
            target = regions[0]  # Fallback to Delhi NCR
            
        base_aqi = target.current_aqi
        hourly_points: List[HourlyForecastPoint] = []
        
        # Diurnal atmospheric curve (higher in morning/evening inversions, lower mid-day)
        diurnal_factors = [
            ("04:00", 0.94), ("05:00", 0.98), ("06:00", 1.02), ("07:00", 1.06),
            ("08:00", 1.10), ("09:00", 1.12), ("10:00", 1.08), ("11:00", 1.04),
            ("12:00", 1.00), ("13:00", 0.97), ("14:00", 0.93), ("15:00", 0.91),
            ("16:00", 0.95), ("17:00", 1.02), ("18:00", 1.09), ("19:00", 1.15),
            ("20:00", 1.18), ("21:00", 1.14),
        ]
        
        for t, factor in diurnal_factors:
            hourly_points.append(HourlyForecastPoint(t=t, aqi=int(base_aqi * factor)))
            
        return HourlyForecastResponse(
            city=target.name,
            state=target.state,
            country="India",
            lat=target.lat,
            lng=target.lng,
            current_aqi=target.current_aqi,
            category=target.status,
            dominant_pollutant=target.dominant_pollutant,
            hourly=hourly_points,
        )

    def generate_legal_notice(self, event_id: str) -> Optional[LegalNoticeDocument]:
        """
        Generates a formal legal regulatory enforcement notice dossier under the
        Air (Prevention and Control of Pollution) Act, 1981 for an environmental event.
        """
        ev = self.enriched_events.get(event_id)
        if not ev:
            return None
            
        now_date = datetime.now(timezone.utc).strftime("%d-%B-%Y")
        notice_num = f"DPCC/ENV/VIG/2026/{event_id.replace('EVT-', '')}"
        
        # Extract evidence strings
        ev_summary = []
        for e in ev.evidence:
            ev_summary.append({"source": str(e.get("label", "")), "details": str(e.get("detail", ""))})
            
        directives = [
            "Immediately CEASE AND DESIST all open combustion and unmitigated emission activities at the specified coordinates.",
            "Deploy continuous mechanical dust misting guns and wet suppression covering a minimum 500-meter radius.",
            "Furnish a written compliance and source disclosure dossier to this authority within 24 hours of notice issuance.",
            "Appear before the Enforcement Officer or designated Environmental Magistrate with operational logs.",
        ]
        
        html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>STATUTORY NOTICE — {notice_num}</title>
<style>
  body {{ font-family: 'Times New Roman', serif; margin: 40px; color: #111; line-height: 1.5; }}
  .header {{ text-align: center; border-bottom: 2px solid #000; padding-bottom: 12px; margin-bottom: 20px; }}
  .gov-title {{ font-size: 16px; font-weight: bold; text-transform: uppercase; }}
  .dept-title {{ font-size: 14px; font-weight: bold; }}
  .ref-row {{ display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 16px; }}
  .subject {{ font-weight: bold; text-decoration: underline; margin: 16px 0; font-size: 14px; text-align: justify; }}
  table {{ width: 100%; border-collapse: collapse; margin: 14px 0; font-size: 12px; }}
  th, td {{ border: 1px solid #333; padding: 6px 10px; text-align: left; }}
  th {{ background: #eee; font-weight: bold; }}
  .directives {{ margin: 12px 0 16px 20px; font-size: 13px; }}
  .directives li {{ margin-bottom: 6px; }}
  .warning-box {{ border: 1.5px dashed #b91c1c; background: #fef2f2; padding: 12px; font-size: 12px; margin: 16px 0; }}
  .sign-box {{ margin-top: 40px; text-align: right; font-size: 13px; }}
  @media print {{
    body {{ margin: 15mm; }}
    .no-print {{ display: none; }}
  }}
</style>
</head>
<body>
<div class="header">
  <div class="gov-title">Government of National Capital Territory of Delhi / State Environmental Authority</div>
  <div class="dept-title">{ev.jurisdiction.upper()}</div>
  <div style="font-size: 11px; margin-top: 4px;">Enforcement & Rapid Vigilance Directorate · Integrated Environmental Command</div>
</div>

<div class="ref-row">
  <div><strong>Event ID:</strong> {ev.id} &nbsp;|&nbsp; <strong>Ref. No:</strong> {notice_num}</div>
  <div><strong>Date of Issuance:</strong> {now_date}</div>
</div>

<div>
  <strong>TO:</strong><br>
  THE OCCUPIER / OPERATOR IN CHARGE<br>
  Facility / Site corresponding to Coordinates ({ev.lat:.4f}° N, {ev.lng:.4f}° E)<br>
  Location: {ev.title}
</div>

<div class="subject">
  SUBJECT: STATUTORY DIRECTION UNDER SECTION 31A OF THE AIR (PREVENTION AND CONTROL OF POLLUTION) ACT, 1981 READ WITH SECTION 5 OF THE ENVIRONMENT (PROTECTION) ACT, 1986 — IMMEDIATE ABATEMENT OF SEVERE ENVIRONMENTAL VIOLATION.
</div>

<p style="text-align: justify; font-size: 13px;">
  <strong>WHEREAS</strong>, the VaayuNetra Autonomous Environmental Intelligence Grid detected an anomalous and critical surge in <strong>{ev.pollutant}</strong> concentrations reaching <strong>{ev.peakValue} {ev.unit}</strong> (local baseline: {ev.baseline} {ev.unit}, statistical anomaly: {ev.anomalyScore}σ) originating from your immediate premises/vicinity on {ev.detectedAt};
</p>

<p style="text-align: justify; font-size: 13px;">
  <strong>AND WHEREAS</strong>, multi-source corroboration confirms significant toxic plume dispersion impacting an estimated population of <strong>{ev.exposure.get('population', 0):,} individuals</strong> and <strong>{ev.exposure.get('schools', 0)} schools / {ev.exposure.get('hospitals', 0)} healthcare centers</strong> downwind;
</p>

<div style="font-size: 13px; font-weight: bold; margin-top: 10px;">MULTI-SOURCE EVIDENCE LINEAGE:</div>
<table>
  <thead>
    <tr><th>Evidence Type</th><th>Monitoring Instrument / Source</th><th>Observed Findings</th></tr>
  </thead>
  <tbody>
    {"".join(f"<tr><td>{e.get('type', '').upper()}</td><td>{e.get('label', '')}</td><td>{e.get('detail', '')}</td></tr>" for e in ev.evidence)}
  </tbody>
</table>

<div style="font-size: 13px; font-weight: bold;">DIRECTIVES & IMMEDIATE ACTIONS REQUIRED:</div>
<ol class="directives">
  {"".join(f"<li>{d}</li>" for d in directives)}
</ol>

<div class="warning-box">
  <strong>PENAL NOTICE:</strong> Take note that non-compliance with the above statutory directions within <strong>24 HOURS</strong> will result in sealing of premises, disconnection of electricity/water utilities under Section 31A of the Air Act 1981, prosecution under Section 37 (punishable with imprisonment up to 6 years), and daily Environmental Compensation of up to ₹1,00,000/- under the Polluter Pays Principle.
</div>

<div class="sign-box">
  <div style="font-weight: bold;">(Authorized Signatory)</div>
  <div>Member Secretary / Designated Competent Authority</div>
  <div>{ev.jurisdiction}</div>
</div>
</body>
</html>"""

        # Generate bilingual statutory text via Gemini service
        bilingual_data = generate_bilingual_statutory_text(
            event_id=ev.id,
            event_title=ev.title,
            pollutant=ev.pollutant,
            peak_value=ev.peakValue,
            unit=ev.unit,
            baseline=ev.baseline,
            anomaly_score=ev.anomalyScore,
            lat=ev.lat,
            lng=ev.lng,
            jurisdiction=ev.jurisdiction,
            impacted_schools=ev.exposure.get("schools", 0),
            impacted_hospitals=ev.exposure.get("hospitals", 0),
            impacted_population=ev.exposure.get("population", 0),
        )

        return LegalNoticeDocument(
            notice_id=f"NOT-{ev.id}",
            event_id=ev.id,
            reference_no=notice_num,
            issuing_authority=ev.jurisdiction,
            recipient=f"Site In-charge ({ev.title})",
            issued_at=now_date,
            subject=f"Statutory Notice under Section 31A Air Act 1981 — {ev.title}",
            event_title=ev.title,
            severity=ev.severity,
            coordinates=f"{ev.lat:.4f}, {ev.lng:.4f}",
            peak_pollutant=f"{ev.pollutant} {ev.peakValue} {ev.unit}",
            baseline=f"{ev.baseline} {ev.unit}",
            anomaly=f"{ev.anomalyScore}σ",
            evidence_summary=ev_summary,
            impact_summary=ev.exposure,
            directives=directives,
            compliance_deadline_hours=24,
            penal_provisions="Section 37 Air Act 1981 & Section 15 Environment (Protection) Act 1986",
            html_document=html_doc,
            hindi_document=bilingual_data["hindi_document"],
            gemini_reasoning=bilingual_data["gemini_reasoning"],
            statutory_citation="Section 31A, Air (Prevention and Control of Pollution) Act, 1981",
        )

    def get_alerts(self) -> List[AlertItem]:
        """Returns urgent operational alerts visible to authority control rooms."""
        now_iso = datetime.now(timezone.utc).isoformat()
        if not self.alerts:
            self.alerts = [
                AlertItem(
                    id="ALT-101",
                    event_id="EVT-2026-0847",
                    title="CRITICAL: Landfill Combustion Plume Detected",
                    severity="CRITICAL",
                    message="Severe PM2.5 spike (312 µg/m³) detected at Okhla sector. Downwind plume expanding towards 6 schools.",
                    created_at=now_iso,
                    acknowledged=False,
                    authority="MCD Solid Waste & Fire Vigilance",
                ),
                AlertItem(
                    id="ALT-102",
                    event_id="EVT-2026-0841",
                    title="HIGH: Unmitigated Road Dust Corridor",
                    severity="HIGH",
                    message="PM10 concentration 428 µg/m³ along Sarita Vihar transit stretch. Anti-smog suppression required.",
                    created_at=now_iso,
                    acknowledged=False,
                    authority="PWD Dust Mitigation",
                ),
                AlertItem(
                    id="ALT-103",
                    event_id="EVT-2026-0839",
                    title="MODERATE: NO2 Peak Inversion",
                    severity="MODERATE",
                    message="Elevated nitrogen dioxide at ITO junction under low mixing height. Traffic diversion advised.",
                    created_at=now_iso,
                    acknowledged=True,
                    authority="Delhi Traffic Police",
                ),
            ]
        return self.alerts

    def acknowledge_alert(self, alert_id: str) -> Optional[AlertItem]:
        for alt in self.alerts:
            if alt.id == alert_id:
                alt.acknowledged = True
                return alt
        return None

    def record_sensor_data(self, data: SensorDataInput) -> Dict[str, Any]:
        """Records normalized sensor reading as specified in docs/api.md."""
        self.sensor_readings.append(data)
        return {
            "status": "accepted",
            "sensor_id": data.sensor_id,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "quality_flag": data.quality_flag,
        }

    def get_corridor_events(self, corridor_id: str) -> List[EnrichedEventItem]:
        """Returns active events intersecting specified corridor as per docs/api.md."""
        results = []
        c_lower = corridor_id.lower()
        for ev in self.enriched_events.values():
            corridors = ev.exposure.get("corridors", [])
            if any(c_lower in str(c).lower() for c in corridors):
                results.append(ev)
        return results


# Global singleton instance
incident_manager = IncidentManager()
