# VaayuNetra - Environmental Intelligence Core

Modular FastAPI backend for real-time atmospheric pollution tracking, satellite thermal anomaly correlation, and downwind Gaussian plume dispersion modeling.

---

## Plug-and-Socket Architecture

```
                       ┌─────────────────────────────────────────┐
                       │   VaayuNetra Core Engine (FastAPI)     │
                       └───────────────────┬─────────────────────┘
                                           │
       ┌───────────────────┬───────────────┴───────────────┬───────────────────┐
       ▼                   ▼                               ▼                   ▼
┌──────────────┐   ┌──────────────┐                ┌──────────────┐    ┌──────────────┐
│   Socket 1   │   │   Socket 2   │                │   Socket 3   │    │   Socket 4   │
│ Live Weather │   │ NASA FIRMS   │                │ Ground IoT   │    │  Dispersion  │
│ (Open-Meteo) │   │ (VIIRS/SNPP) │                │ Sensor Feed  │    │  Plume Cone  │
└──────────────┘   └──────────────┘                └──────────────┘    └──────────────┘
```

1. **Socket 1: Weather Vector (`services/weather.py`)**
   - Ingests real-time wind speed (`wind_speed_10m`) and direction (`wind_direction_10m`) from Open-Meteo API.
   - Resilient fallback (`wind_speed: 12.0`, `wind_direction: 220.0`, `temp: 28.0`) on network timeout.
2. **Socket 2: Satellite Thermal Anomaly (`services/firms.py`)**
   - Hook for NASA FIRMS (Fire Information for Resource Management System) VIIRS/MODIS satellite passes.
   - Non-blocking error handling returning detection confidence, sensor type, and distance.
3. **Socket 3: Ground IoT Baseline (`services/sensor_stream.py`)**
   - Queries Sensor.Community open IoT network with bounding-box spatial filtering.
   - Automatic failover to 3 localized synthetic IoT sensor nodes (`~138 µg/m³ PM2.5`) to guarantee feed reliability.
4. **Socket 4: Gaussian Plume Generator (`models/dispersion.py`)**
   - Computes downwind smoke heading: `(wind_direction + 180) % 360`.
   - Projects an expanding 30-degree dispersion cone GeoJSON Polygon forward proportional to `wind_speed * hours`.
   - Includes ray-casting point-in-polygon containment detection to alert citizens inside active plumes.
5. **Socket 5: Vulnerable Community Receptors (`services/receptors.py`)**
   - Accepts plume polygon coordinates and queries OpenStreetMap Overpass API via `(poly:"lat lon...")`.
   - Discovers schools, hospitals, clinics, and kindergartens in the plume path.
   - Computes a composite `vulnerability_score` (0-100) and `risk_level` (Low, Moderate, High, Critical) with automatic fallback.
6. **Socket 6: Regional Atmospheric Column Context (`services/cams_air.py`)**
   - Ingests hourly Nitrogen Dioxide (NO2) and Aerosol Optical Depth (AOD) from Open-Meteo Air Quality / CAMS.
   - Classifies regional air column (Biomass Burning vs Urban Traffic Smog vs Compound Inversion).
7. **Vision Model: Evidence Checker (`models/vision.py`)**
   - Inspects photographic evidence bytes to verify active biomass burning / smoke detection.

---

## Quickstart & Execution

### 1. Activate Environment
```powershell
# In PowerShell:
.\venv\Scripts\activate
```

### 2. Run Verification Test Suite
```powershell
python test_backend.py
```

### 3. Launch Development Server
```powershell
uvicorn main:app --reload --port 8000
# or
python main.py
```
API Documentation will be live at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## API Endpoints

### 1. Health Check
- **`GET /`**
  - Returns engine status and readiness of all 4 sockets.

### 2. Report Incident (Form Upload)
- **`POST /api/v1/report`**
  - Form Fields: `latitude: float`, `longitude: float`, `category: str`, `file: UploadFile`
  - High-performance non-blocking pipeline:
    - **Stage 1 (Parallel Fan-Out via `asyncio.gather`)**:
      - Image verification (`models/vision.py`)
      - Real-time wind vectors (`services/weather.py`, 2.5s cap)
      - Satellite thermal anomaly (`services/firms.py`, 2.5s cap)
      - Regional gas column (`services/cams_air.py`, 2.5s cap)
    - **Stage 2**: Gaussian plume 2D dispersion cone projection (`models/dispersion.py`)
    - **Stage 3**: Downwind receptor identification (`services/receptors.py`, 2.5s cap)
    - **Stage 4**: Merge into unified `IncidentTicketResponse` (sub-4s latency).
  - Returns unified `IncidentTicketResponse`:
    ```json
    {
      "ticket_id": "VN-102",
      "timestamp": "2026-09-06T00:45:11Z",
      "category": "landfill_fire",
      "latitude": 28.7041,
      "longitude": 77.1025,
      "verification": {
        "vision_verified": true,
        "vision_confidence": 0.91,
        "satellite_thermal_match": true,
        "thermal_distance_m": 420.0
      },
      "atmospheric": {
        "wind_speed_kmh": 3.6,
        "wind_direction_deg": 37.0,
        "temperature_c": 26.2,
        "regional_no2_ugm3": 86.6,
        "aerosol_optical_depth": 0.44
      },
      "impact": {
        "vulnerability_score": 100,
        "alert_priority": "CRITICAL",
        "impacted_receptors": [
          {
            "name": "Sarvodaya Bal Vidyalaya",
            "amenity_type": "school",
            "distance_m": 480.2
          }
        ]
      },
      "plume_geojson": { ... }
    }
    ```

### 3. Citizen Feed & Plume Collision Alert
- **`GET /api/v1/feed?lat={lat}&lon={lon}`**
  - Delivers localized street PM2.5 baseline, lists active incidents, and alerts via `active_warnings` list indicating whether passed coordinates fall inside any downwind plume cone.

## Flutter Mobile Client (`client/`)

The client provides an ambient environmental intelligence interface communicating directly with the FastAPI backend.

### Screen Architecture

1. **Radar Screen (`lib/screens/radar_screen.dart`)**:
   - Live street-level PM2.5 gauge with dynamic AQI severity coloring.
   - Nearby IoT sensor nodes list with distances and particulate readings.
   - High-contrast critical warning banner triggered whenever user coordinates intersect an active downwind plume.
   - In-app server host configuration modal (`10.0.2.2:8000` for emulator, `127.0.0.1:8000` for desktop/web, or LAN IP).

2. **Report Screen (`lib/screens/report_screen.dart`)**:
   - Camera and gallery image picker for photographic proof.
   - Incident classification dropdown (Biomass, Agricultural Stubble, Landfill Fire, Industrial Smog).
   - Coordinate entry with GPS one-tap auto-detection.
   - Dispatches multipart form data to `POST /api/v1/report` and renders the real-time verified ticket summary card.

3. **Municipal Map Screen (`lib/screens/municipal_map_screen.dart`)**:
   - Powered by `flutter_map` (OpenStreetMap).
   - Renders incident origin flame markers (Points).
   - Draws downwind 30-degree expanding dispersion cones (Polygons) color-coded by vulnerability severity.
   - Interactive inspection card and "Pitch Demo Spike" floating action button.

4. **Models & Services (`lib/models/ticket.dart` & `lib/services/api_service.dart`)**:
   - Strict Dart data models mapping 1:1 to FastAPI Pydantic v2 schemas.
   - Multi-platform host resolution (`kIsWeb`, `Platform.isAndroid`, LAN).

### Running the Flutter Client
```powershell
cd client
flutter pub get
flutter run
```
