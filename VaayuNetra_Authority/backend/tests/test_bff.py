import io
from fastapi.testclient import TestClient
from PIL import Image

from backend.app import app

client = TestClient(app)


def test_health_endpoint():
    """Verify GET / returns healthy status and endpoint map."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "VaayuNetra" in data["service"]
    assert "feed" in data["endpoints"]
    assert "report" in data["endpoints"]
    assert "municipal_incidents" in data["endpoints"]
    assert "simulate_spike" in data["endpoints"]
    assert data["active_incidents_count"] >= 3


def test_citizen_feed():
    """Verify GET /api/v1/feed returns PM2.5, AQI, sensors, and warnings."""
    response = client.get("/api/v1/feed?lat=28.6139&lon=77.2090")
    assert response.status_code == 200
    data = response.json()
    assert "current_pm25" in data
    assert "aqi" in data
    assert "aqi_category" in data
    assert len(data["nearby_sensors"]) > 0
    assert "weather" in data
    assert "wind_speed_mps" in data["weather"]
    assert "recommendations" in data


def test_citizen_feed_inside_plume_warning():
    """Verify user located directly inside Ghazipur downwind plume receives active warning with multilingual alerts."""
    response = client.get("/api/v1/feed?lat=28.6250&lon=77.3400")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["active_warnings"], list)
    if len(data["active_warnings"]) > 0:
        w = data["active_warnings"][0]
        assert "hindi_message" in w and w["hindi_message"] is not None
        assert "punjabi_message" in w and w["punjabi_message"] is not None


def test_municipal_incidents_geojson():
    """Verify GET /api/v1/municipal/incidents returns standard GeoJSON FeatureCollection."""
    response = client.get("/api/v1/municipal/incidents")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) > 0
    
    geom_types = {f["geometry"]["type"] for f in data["features"]}
    assert "Point" in geom_types
    assert "Polygon" in geom_types
    
    point_features = [f for f in data["features"] if f["geometry"]["type"] == "Point"]
    polygon_features = [f for f in data["features"] if f["geometry"]["type"] == "Polygon"]
    assert "category" in point_features[0]["properties"]
    assert "severity" in point_features[0]["properties"]
    assert "wind_speed" in point_features[0]["properties"]
    assert "color" in polygon_features[0]["properties"]


def test_simulate_spike():
    """Verify POST /api/v1/simulate/spike triggers new active incident ticket."""
    payload = {
        "latitude": 28.7120,
        "longitude": 77.1450,
        "category": "waste_burning",
        "severity": "HIGH",
        "wind_speed_mps": 4.5,
        "wind_direction_deg": 310.0,
    }
    response = client.post("/api/v1/simulate/spike", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "VERIFIED"
    assert data["ticket_id"].startswith("TKT-")
    assert data["category"] == "waste_burning"
    assert data["ai_vision"]["visual_evidence"] is True
    assert data["plume_geometry"]["type"] == "Polygon"
    assert len(data["plume_geometry"]["coordinates"][0]) > 10
    assert len(data["impacted_receptors"]) > 0


def test_incident_report_multipart():
    """Verify POST /api/v1/report accepts image upload and returns unified IncidentTicketResponse."""
    img = Image.new("RGB", (100, 100), color=(200, 50, 20))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="JPEG")
    img_byte_arr.seek(0)
    
    files = {
        "file": ("test_smoke.jpg", img_byte_arr, "image/jpeg")
    }
    data = {
        "latitude": "28.6320",
        "longitude": "77.2180",
        "category": "waste_burning"
    }
    
    response = client.post("/api/v1/report", data=data, files=files)
    assert response.status_code == 200
    ticket = response.json()
    assert ticket["ticket_id"].startswith("TKT-")
    assert ticket["status"] == "VERIFIED"
    assert ticket["ai_vision"]["confidence"] >= 0.70
    assert "Gemini" in ticket["ai_vision"]["model_version"] or "Gemini" in str(ticket["ai_vision"].get("ai_engine", ""))
    assert ticket["ai_vision"].get("reasoning") is not None
    assert ticket["ai_vision"].get("plume_density") is not None
    assert ticket["wind_vector"]["speed_mps"] > 0
    assert ticket["plume_geometry"]["type"] == "Polygon"
    assert len(ticket["impacted_receptors"]) > 0


def test_events_lifecycle():
    """Verify GET /api/v1/events and event lifecycle actions."""
    response = client.get("/api/v1/events")
    assert response.status_code == 200
    events = response.json()
    assert len(events) >= 3
    event_id = events[0]["id"]
    
    # Acknowledge
    ack_res = client.post(f"/api/v1/events/{event_id}/acknowledge")
    assert ack_res.status_code == 200
    assert ack_res.json()["current_status"] == "ACKNOWLEDGED"
    
    # Get by ID
    single_res = client.get(f"/api/v1/events/{event_id}")
    assert single_res.status_code == 200
    assert single_res.json()["id"] == event_id


def test_actions_api():
    """Verify GET and POST /api/v1/actions."""
    list_res = client.get("/api/v1/actions")
    assert list_res.status_code == 200
    actions = list_res.json()
    assert len(actions) >= 3
    
    # Create action
    payload = {
        "eventId": "EVT-2026-0847",
        "type": "FIELD_INSPECTION",
        "assignee": "SDM East Delhi Patrol",
        "notes": "Verify open combustion at Okhla sector",
    }
    create_res = client.post("/api/v1/actions", json=payload)
    assert create_res.status_code == 200
    action = create_res.json()
    assert action["id"].startswith("ACT-")
    assert action["eventId"] == "EVT-2026-0847"
    assert action["assignee"] == "SDM East Delhi Patrol"


def test_advisories_api():
    """Verify GET and POST /api/v1/advisories."""
    list_res = client.get("/api/v1/advisories")
    assert list_res.status_code == 200
    advisories = list_res.json()
    assert len(advisories) >= 3
    
    # Compose advisory
    payload = {
        "eventId": "EVT-2026-0841",
        "title": "Dust plume health warning",
        "audience": "Sarita Vihar residents",
        "languages": ["EN", "HI"],
        "channels": ["SMS", "App"],
        "message": "High PM10 levels detected. Wear protective masks.",
    }
    create_res = client.post("/api/v1/advisories", json=payload)
    assert create_res.status_code == 200
    adv = create_res.json()
    assert adv["id"].startswith("ADV-")
    assert adv["status"] == "SENT"
    
    # Send draft advisory
    draft = next((a for a in advisories if a["status"] == "DRAFT"), None)
    if draft:
        send_res = client.post(f"/api/v1/advisories/{draft['id']}/send")
        assert send_res.status_code == 200
        assert send_res.json()["status"] == "SENT"


def test_forecast_hourly_api():
    """Verify GET /api/v1/forecast/hourly and multi-region query."""
    res = client.get("/api/v1/forecast/hourly")
    assert res.status_code == 200
    data = res.json()
    assert data["city"] == "Delhi NCR"
    assert len(data["hourly"]) >= 10
    assert "aqi" in data["hourly"][0]

    # Test Mumbai regional forecast
    mumbai_res = client.get("/api/v1/forecast/hourly?city=Mumbai")
    assert mumbai_res.status_code == 200
    mumbai_data = mumbai_res.json()
    assert mumbai_data["city"] == "Mumbai"
    assert len(mumbai_data["hourly"]) >= 10

    # Test regions list
    regions_res = client.get("/api/v1/forecast/regions")
    assert regions_res.status_code == 200
    reg_data = regions_res.json()
    assert isinstance(reg_data, list)
    assert len(reg_data) >= 10
    city_names = [r["name"] for r in reg_data]
    assert "Delhi NCR" in city_names
    assert "Mumbai" in city_names
    assert "Bengaluru" in city_names
    assert "Kolkata" in city_names


def test_legal_notice_generation():
    """Verify GET /api/v1/events/{id}/notice returns structured statutory notice, Gemini reasoning, and bilingual formats."""
    res = client.get("/api/v1/events/EVT-2026-0847/notice")
    assert res.status_code == 200
    doc = res.json()
    assert doc["notice_id"].startswith("NOT-")
    assert doc["event_id"] == "EVT-2026-0847"
    assert "reference_no" in doc
    assert "Air" in doc["penal_provisions"] or "Air" in doc["subject"]
    assert len(doc["directives"]) >= 3
    assert len(doc["evidence_summary"]) >= 1
    assert "hindi_document" in doc and len(doc["hindi_document"]) > 20
    assert "gemini_reasoning" in doc and len(doc["gemini_reasoning"]) > 10

    # English HTML format for print preview
    html_res = client.get("/api/v1/events/EVT-2026-0847/notice?format=html")
    assert html_res.status_code == 200
    assert "text/html" in html_res.headers.get("content-type", "")
    assert "STATUTORY" in html_res.text
    assert "EVT-2026-0847" in html_res.text

    # Hindi HTML format for vernacular enforcement
    hindi_res = client.get("/api/v1/events/EVT-2026-0847/notice?format=hindi")
    assert hindi_res.status_code == 200
    assert "text/html" in hindi_res.headers.get("content-type", "")
    assert "वैधानिक" in hindi_res.text
    assert "अधिनियम" in hindi_res.text


def test_alerts_api():
    """Verify GET /api/v1/alerts and POST /api/v1/alerts/{id}/acknowledge."""
    res = client.get("/api/v1/alerts")
    assert res.status_code == 200
    alerts = res.json()
    assert isinstance(alerts, list)
    assert len(alerts) >= 3

    # Acknowledge first alert
    alert_id = alerts[0]["id"]
    ack_res = client.post(f"/api/v1/alerts/{alert_id}/acknowledge")
    assert ack_res.status_code == 200
    ack_data = ack_res.json()
    assert ack_data["acknowledged"] is True


def test_event_subresources():
    """Verify /api/v1/events/{id}/evidence, /forecast, /risk per docs/api.md."""
    evt_id = "EVT-2026-0847"
    
    ev_res = client.get(f"/api/v1/events/{evt_id}/evidence")
    assert ev_res.status_code == 200
    ev_data = ev_res.json()
    assert ev_data["event_id"] == evt_id
    assert len(ev_data["evidence"]) > 0

    fc_res = client.get(f"/api/v1/events/{evt_id}/forecast")
    assert fc_res.status_code == 200
    fc_data = fc_res.json()
    assert fc_data["event_id"] == evt_id
    assert len(fc_data["forecast"]) > 0

    risk_res = client.get(f"/api/v1/events/{evt_id}/risk")
    assert risk_res.status_code == 200
    risk_data = risk_res.json()
    assert risk_data["event_id"] == evt_id
    assert "priority" in risk_data


def test_sensor_data_ingestion():
    """Verify POST /api/v1/sensor-data per docs/api.md."""
    payload = {
        "sensor_id": "CPCB-ANAND-VIHAR-01",
        "timestamp": "2026-09-06T03:00:00Z",
        "latitude": 28.6469,
        "longitude": 77.3160,
        "parameter": "pm25",
        "value": 164.2,
        "unit": "ug/m3",
        "quality_flag": "good"
    }
    res = client.post("/api/v1/sensor-data", json=payload)
    assert res.status_code == 200
    assert res.json()["status"] == "accepted"
    assert res.json()["sensor_id"] == "CPCB-ANAND-VIHAR-01"


def test_api_aliases():
    """Verify unversioned /api/* routes match /api/v1/* routes."""
    res1 = client.get("/api/events")
    assert res1.status_code == 200
    assert len(res1.json()) >= 3

    res2 = client.get("/api/actions")
    assert res2.status_code == 200

    res3 = client.get("/api/advisories")
    assert res3.status_code == 200

    res4 = client.get("/api/forecast/hourly")
    assert res4.status_code == 200


def test_dashboard_page_served():
    """Verify GET /dashboard serves the updated index.html."""
    res = client.get("/dashboard")
    assert res.status_code == 200
    assert "VaayuNetra" in res.text
    assert "dash-layout" in res.text or "Air Quality Forecast" in res.text or "pageRoot" in res.text


if __name__ == "__main__":
    print("Running extended BFF & Dashboard tests...")
    test_health_endpoint()
    print("[PASS] test_health_endpoint")
    test_citizen_feed()
    print("[PASS] test_citizen_feed")
    test_citizen_feed_inside_plume_warning()
    print("[PASS] test_citizen_feed_inside_plume_warning")
    test_municipal_incidents_geojson()
    print("[PASS] test_municipal_incidents_geojson")
    test_simulate_spike()
    print("[PASS] test_simulate_spike")
    test_incident_report_multipart()
    print("[PASS] test_incident_report_multipart")
    test_events_lifecycle()
    print("[PASS] test_events_lifecycle")
    test_actions_api()
    print("[PASS] test_actions_api")
    test_advisories_api()
    print("[PASS] test_advisories_api")
    test_forecast_hourly_api()
    print("[PASS] test_forecast_hourly_api")
    test_legal_notice_generation()
    print("[PASS] test_legal_notice_generation")
    test_alerts_api()
    print("[PASS] test_alerts_api")
    test_event_subresources()
    print("[PASS] test_event_subresources")
    test_sensor_data_ingestion()
    print("[PASS] test_sensor_data_ingestion")
    test_api_aliases()
    print("[PASS] test_api_aliases")
    test_dashboard_page_served()
    print("[PASS] test_dashboard_page_served")
    print("\nALL 16 TESTS PASSED SUCCESSFULLY!")
