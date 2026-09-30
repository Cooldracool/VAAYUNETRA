"""Automated Verification Suite for VaayuNetra High-Performance Async Backend (Sockets 1-6)."""

import asyncio
import io
import json
import time
from fastapi.testclient import TestClient

from main import app, INCIDENTS_DB
from models.dispersion import calculate_plume_cone, is_point_in_plume
from models.vision import verify_image_evidence
from schemas.responses import (
    AtmosphericSummary,
    ImpactAssessment,
    IncidentTicketResponse,
    VerificationSummary,
)
from services.cams_air import get_atmospheric_context
from services.firms import check_thermal_hotspots
from services.receptors import get_vulnerable_receptors
from services.sensor_stream import get_nearby_sensors
from services.weather import get_live_weather


async def test_async_services():
    print("=" * 60)
    print("RUNNING ASYNC SERVICE SOCKET VERIFICATIONS")
    print("=" * 60)

    # 1. Test Weather Service (Socket 1)
    print("\n[1/6] Testing Socket 1 - Async Weather Service (2.5s cap)...")
    t0 = time.perf_counter()
    weather = await get_live_weather(28.6139, 77.2090)
    dt = time.perf_counter() - t0
    print(f"  Weather response in {dt:.2f}s:", weather)
    assert "wind_speed_10m" in weather
    assert "wind_direction_10m" in weather
    assert "source" in weather
    assert dt < 3.5, f"Weather took too long: {dt}s"
    print("  [PASS] Socket 1 (Weather) passed!")

    # 2. Test NASA FIRMS Service (Socket 2)
    print("\n[2/6] Testing Socket 2 - Async Satellite Thermal Anomaly...")
    t0 = time.perf_counter()
    firms = await check_thermal_hotspots(28.6139, 77.2090)
    dt = time.perf_counter() - t0
    print(f"  FIRMS response in {dt:.2f}s:", firms)
    assert firms["hotspot_detected"] is True
    assert firms["sensor"] == "VIIRS_SNPP"
    assert firms["confidence"] == "nominal"
    assert "distance_m" in firms
    print("  [PASS] Socket 2 (FIRMS) passed!")

    # 3. Test Ground IoT Sensor Stream (Socket 3)
    print("\n[3/6] Testing Socket 3 - Async Ground IoT Baseline (2.0s cap)...")
    t0 = time.perf_counter()
    sensors = await get_nearby_sensors(28.6139, 77.2090)
    dt = time.perf_counter() - t0
    print(f"  Received {len(sensors)} sensor nodes in {dt:.2f}s. Sample:", sensors[0])
    assert len(sensors) >= 3
    assert "pm2_5" in sensors[0]
    assert "distance_km" in sensors[0]
    assert dt < 3.0, f"Sensor stream took too long: {dt}s"
    print("  [PASS] Socket 3 (IoT Sensors) passed!")

    # 4. Test Gaussian Plume Dispersion Model (Socket 4)
    print("\n[4/6] Testing Socket 4 - Gaussian Plume Generator...")
    plume = calculate_plume_cone(
        source_lat=28.6139,
        source_lon=77.2090,
        wind_speed_kmh=20.0,
        wind_dir_deg=270.0,
        hours=4.0,
    )
    assert plume["type"] == "Feature"
    assert plume["geometry"]["type"] == "Polygon"
    assert len(plume["geometry"]["coordinates"][0]) >= 10
    props = plume["properties"]
    assert props["heading_deg"] == (270.0 + 180.0) % 360.0  # 90.0 (East)
    assert props["distance_km"] == 80.0
    print(f"  Computed Plume Heading: {props['heading_deg']} deg, Distance: {props['distance_km']} km")

    pt_inside_lat, pt_inside_lon = 28.6139, 77.2090 + 0.1
    assert is_point_in_plume(pt_inside_lat, pt_inside_lon, plume) is True
    pt_outside_lat, pt_outside_lon = 28.6139, 77.2090 - 0.5
    assert is_point_in_plume(pt_outside_lat, pt_outside_lon, plume) is False
    print("  [PASS] Socket 4 (Dispersion Model) passed!")

    # 5. Test Vulnerable Community Receptors (Socket 5)
    print("\n[5/6] Testing Socket 5 - Async Vulnerable Receptors (2.5s cap)...")
    plume_coords = plume["geometry"]["coordinates"]
    t0 = time.perf_counter()
    receptors = await get_vulnerable_receptors(plume_coords)
    dt = time.perf_counter() - t0
    print(f"  Receptors response in {dt:.2f}s:", {
        "vulnerability_score": receptors.get("vulnerability_score"),
        "risk_level": receptors.get("risk_level"),
        "total_receptors": receptors.get("total_receptors"),
        "source": receptors.get("source"),
    })
    assert "vulnerability_score" in receptors
    assert receptors["vulnerability_score"] >= 0.0
    assert "receptors" in receptors
    assert len(receptors["receptors"]) >= 2
    assert dt < 3.5, f"Overpass query took too long: {dt}s"
    print("  [PASS] Socket 5 (Vulnerable Receptors) passed!")

    # 6. Test Regional Atmospheric Air Column Context (Socket 6)
    print("\n[6/6] Testing Socket 6 - Async Regional Atmospheric Air Column (2.5s cap)...")
    t0 = time.perf_counter()
    atmosphere = await get_atmospheric_context(28.6139, 77.2090)
    dt = time.perf_counter() - t0
    print(f"  Atmospheric context in {dt:.2f}s:", atmosphere)
    assert "nitrogen_dioxide" in atmosphere
    assert "aerosol_optical_depth" in atmosphere
    assert "air_column_classification" in atmosphere
    assert dt < 3.5, f"CAMS atmospheric query took too long: {dt}s"
    print("  [PASS] Socket 6 (Atmospheric Context) passed!")


def test_fastapi_endpoints():
    print("\n" + "=" * 60)
    print("TESTING FASTAPI NON-BLOCKING ENDPOINTS")
    print("=" * 60)

    client = TestClient(app)

    # 1. Dynamic YOLO Vision Model Verification
    from PIL import Image as PILImage
    import numpy as np
    from database import get_all_incidents, get_active_incidents
    from models.vision import verify_pollution_image

    # 1a. Test empty bytes
    v_empty = verify_image_evidence(b"")
    assert v_empty["verified"] is False
    assert v_empty["confidence"] == 0.0
    assert v_empty["detected_classes"] == []

    # 1b. Test edge case: Clean non-smoke image (solid white)
    buf_clean = io.BytesIO()
    PILImage.new("RGB", (100, 100), color=(255, 255, 255)).save(buf_clean, format="JPEG")
    v_clean = verify_image_evidence(buf_clean.getvalue())
    assert v_clean["verified"] is False
    assert v_clean["confidence"] <= 0.35
    print(f"  Edge Case (Non-smoke): Verified={v_clean['verified']}, Conf={v_clean['confidence']}, Label={v_clean['label']}")

    # 1c. Test synthetic smoke image (biomass burning plume)
    img_smoke = PILImage.new("RGB", (100, 100), color=(140, 120, 95))
    smoke_buf = io.BytesIO()
    img_smoke.save(smoke_buf, format="JPEG")
    smoke_bytes = smoke_buf.getvalue()

    v_smoke = verify_image_evidence(smoke_bytes)
    print(f"  Dynamic YOLO Smoke Analysis: Confidence={v_smoke['confidence']}, Classes={v_smoke['detected_classes']}, Label={v_smoke['label']}")
    assert isinstance(v_smoke["confidence"], float)
    assert 0.0 <= v_smoke["confidence"] <= 1.0
    assert v_smoke["verified"] is True
    assert "detected_classes" in v_smoke
    assert "label" in v_smoke
    print("  [PASS] Local YOLO Vision Model verified!")

    # 2. GET /
    res_root = client.get("/")
    assert res_root.status_code == 200
    root_data = res_root.json()
    assert root_data["status"] == "operational"
    print("  [PASS] GET / returned 200 OK")

    # 3. POST /api/v1/simulate/spike & Database Persistence
    sim_payload = {
        "latitude": 28.6139,
        "longitude": 77.2090,
        "category": "agricultural_stubble_burning",
    }
    t0 = time.perf_counter()
    res_sim = client.post("/api/v1/simulate/spike", json=sim_payload)
    dt_sim = time.perf_counter() - t0
    assert res_sim.status_code == 201
    sim_ticket = res_sim.json()
    assert "ticket_id" in sim_ticket
    assert "verification" in sim_ticket
    assert "atmospheric" in sim_ticket
    assert "impact" in sim_ticket
    print(f"  [PASS] POST /api/v1/simulate/spike executed in {dt_sim:.2f}s | Ticket: {sim_ticket['ticket_id']}")

    # Verify ticket was saved to SQLite database
    db_incidents = get_all_incidents()
    saved_ids = [inc["ticket_id"] for inc in db_incidents]
    assert sim_ticket["ticket_id"] in saved_ids, "Simulation ticket not found in SQLite database!"
    print(f"  [PASS] SQLite persistence confirmed: Ticket {sim_ticket['ticket_id']} persisted in vaayunetra.db")

    # 4. POST /api/v1/report with dynamic image upload & DB persistence
    file_payload = ("biomass_smoke.jpg", io.BytesIO(smoke_bytes), "image/jpeg")
    t0 = time.perf_counter()
    res_report = client.post(
        "/api/v1/report",
        data={"latitude": "28.7041", "longitude": "77.1025", "category": "landfill_fire"},
        files={"file": file_payload},
    )
    dt_report = time.perf_counter() - t0
    assert res_report.status_code == 201
    report_ticket = res_report.json()

    # Explicit validation of all merged keys
    required_keys = {"ticket_id", "verification", "atmospheric", "impact", "plume_geojson"}
    assert required_keys.issubset(report_ticket.keys()), f"Missing keys: {required_keys - set(report_ticket.keys())}"

    verif = report_ticket["verification"]
    assert isinstance(verif["vision_verified"], bool)
    assert isinstance(verif["vision_confidence"], float)
    assert isinstance(verif["satellite_thermal_match"], bool)
    assert isinstance(verif["thermal_distance_m"], float)

    # Check that report ticket also persisted to SQLite
    db_incidents = get_all_incidents()
    assert any(inc["ticket_id"] == report_ticket["ticket_id"] for inc in db_incidents), "Report ticket not persisted to SQLite!"

    atmos = report_ticket["atmospheric"]
    assert isinstance(atmos["wind_speed_kmh"], float)
    assert isinstance(atmos["wind_direction_deg"], float)
    assert isinstance(atmos["temperature_c"], float)
    assert isinstance(atmos["regional_no2_ugm3"], float)
    assert isinstance(atmos["aerosol_optical_depth"], float)

    impact = report_ticket["impact"]
    assert isinstance(impact["vulnerability_score"], int)
    assert impact["alert_priority"] in {"LOW", "MODERATE", "HIGH", "CRITICAL"}
    assert isinstance(impact["impacted_receptors"], list)

    print(f"  [PASS] POST /api/v1/report parallel fan-out executed in {dt_report:.2f}s!")
    print(f"         Ticket ID: {report_ticket['ticket_id']} | Priority: {impact['alert_priority']} | Receptors: {len(impact['impacted_receptors'])}")
    assert dt_report < 6.0, f"Parallel execution took too long: {dt_report}s (must eliminate 25s latency spike)"

    # 5. GET /api/v1/feed and Multi-User Citizen Alerting
    # Test feed right downwind from the simulated stubble burning incident (28.6139, 77.2090)
    # Check plume heading to query inside the cone
    plume_coords = sim_ticket["plume_geojson"]["geometry"]["coordinates"][0]
    # Pick a point inside the plume geometry (e.g., centroid or mid-edge coordinate)
    target_lat = (plume_coords[0][1] + plume_coords[len(plume_coords)//2][1]) / 2.0
    target_lon = (plume_coords[0][0] + plume_coords[len(plume_coords)//2][0]) / 2.0

    t0 = time.perf_counter()
    res_feed = client.get(f"/api/v1/feed?lat={target_lat}&lon={target_lon}")
    dt_feed = time.perf_counter() - t0
    assert res_feed.status_code == 200
    feed_data = res_feed.json()
    assert "street_pm2_5" in feed_data
    assert "active_warnings" in feed_data
    assert dt_feed < 3.0, f"Feed took too long: {dt_feed}s"
    print(f"  [PASS] GET /api/v1/feed executed in {dt_feed:.2f}s | Active Warnings: {len(feed_data['active_warnings'])}")
    if feed_data["active_warnings"]:
        warning = feed_data["active_warnings"][0]
        safe_adv = warning['advisory'].encode('ascii', errors='replace').decode('ascii')
        print(f"  Plume warning advisory: {safe_adv}")
        assert "Active Smoke Plume Alert:" in warning["advisory"]
        assert "upwind from your location" in warning["advisory"]
        print("  [PASS] Citizen plume warning format verified!")

    # 6. GET /api/v1/municipal/incidents querying SQLite database
    res_muni = client.get("/api/v1/municipal/incidents")
    assert res_muni.status_code == 200
    muni_geojson = res_muni.json()
    assert muni_geojson["type"] == "FeatureCollection"
    assert len(muni_geojson["features"]) >= 2
    print(f"  [PASS] GET /api/v1/municipal/incidents returned FeatureCollection with {len(muni_geojson['features'])} features from SQLite")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ZERO LATENCY SPIKES & PERSISTENCE CONFIRMED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_async_services())
    test_fastapi_endpoints()
