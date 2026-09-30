# VaayuNetra (वायुनेत्र)

> **Multi-Source Environmental Intelligence & Hyper-Local Pollution-Event Decision Support Platform**  


[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://python.org)
[![GeoJSON](https://img.shields.io/badge/GeoJSON-RFC_7946-2c3e50.svg?style=flat)](https://datatracker.ietf.org/doc/html/rfc7946)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9.4-199900.svg?style=flat&logo=leaflet&logoColor=white)](https://leafletjs.com)
[![Render](https://img.shields.io/badge/Render-Live%20Deployment-46E3B7.svg?style=flat&logo=render&logoColor=white)](https://vaayunetra-authority.onrender.com/dashboard)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat)](LICENSE)

> 🚀 **Live Production Deployment:** [https://vaayunetra-authority.onrender.com/dashboard](https://vaayunetra-authority.onrender.com/dashboard)  
> 📖 **Interactive Swagger / API Docs:** [https://vaayunetra-authority.onrender.com/docs](https://vaayunetra-authority.onrender.com/docs)  
> 🩺 **System Health & Discovery:** [https://vaayunetra-authority.onrender.com/](https://vaayunetra-authority.onrender.com/)

---

## 📌 Executive Summary

Conventional environmental monitoring platforms are largely **AQI-centric, regional, and reactive**. They aggregate historical sensor data across wide metropolitan areas and display static charts hours after pollution spikes have already exposed populations.

**VaayuNetra** shifts environmental management from retrospective AQI tracking to **emerging event intelligence**:
1. **Detects** hyper-local pollution events in near-real-time by fusing ground sensors, citizen reports, computer vision, satellite thermal anomalies, and meteorology.
2. **Models** atmospheric dispersion using physics-guided Gaussian plume algorithms and live wind vectors.
3. **Projects** downwind exposure against sensitive receptors (schools, pediatric centers, hospitals, care homes) with estimated time of arrival (ETA).
4. **Calculates** calibrated priority scores and **routes actionable dispatch directives** to the responsible municipal or environmental authority.
5. **Empowers Citizens** via a hyper-local Home Radar that delivers street-level air quality, inside-plume hazard warnings, and actionable health advisories.

---

## 🔄 The Core Intelligence Loop

VaayuNetra processes environmental data through an end-to-end, multi-stage closed loop:

```
[ Data Sources ]
  • Official CAAQMS (CPCB/SPCB)
  • Hyper-Local IoT Sensor Grid
  • Geotagged Citizen Photo Reports
  • NASA FIRMS Satellite Thermal Hotspots
  • Open-Meteo High-Resolution Wind & Weather
  • Vulnerable Receptors Catalog (OSM / GIS)
                         │
                         ▼
             ┌───────────────────────┐
             │ Ingest & Normalize    │
             └───────────┬───────────┘
                         │
                         ▼
             ┌───────────────────────┐
             │ Spatial & Temporal    │
             │ Alignment (H3 / Grid) │
             └───────────┬───────────┘
                         │
                         ▼
             ┌───────────────────────┐
             │ Local Baseline &      │
             │ Anomaly Detection     │
             └───────────┬───────────┘
                         │
                         ▼
             ┌───────────────────────┐
             │ Multi-Source Evidence │
             │ Corroboration Engine  │
             └───────────┬───────────┘
                         │
                         ▼
             ┌───────────────────────┐
             │ Gaussian Plume        │
             │ Dispersion Modeling   │
             └───────────┬───────────┘
                         │
                         ▼
             ┌───────────────────────┐
             │ Sensitive Receptor    │
             │ Intersection & Impact │
             └───────────┬───────────┘
                         │
                         ▼
             ┌───────────────────────┐
             │ Priority Scoring &    │
             │ Authority Routing     │
             └───────────┬───────────┘
                         │
                         ▼
             ┌───────────────────────┐
             │ Action Dispatch &     │
             │ Closed-Loop Learning  │
             └───────────────────────┘
```

---

## 🚀 Key Features

### 1. Multi-Source Evidence Corroboration
- **Official & IoT Grid Sensors**: Interpolates street-level PM2.5 concentrations using Inverse Distance Weighting (IDW) calibrated against Indian National AQI breakpoints.
- **Citizen AI Computer Vision**: Lightweight server-side vision engine that analyzes RGB color distributions, luminance variance, and saturation profiles to detect active combustion flares, diffuse smoke plumes, fugitive dust suspensions, and industrial stack emissions.
- **NASA FIRMS Thermal Hotspot Correlation**: Intersects incident coordinates with thermal anomaly detections (MODIS/VIIRS) reporting Brightness Temperature (Kelvin) and Fire Radiative Power (FRP in MW).
- **High-Resolution Meteorology**: Integrates real-time wind speed, wind direction vector, temperature, and relative humidity via Open-Meteo with intelligent in-memory caching and fallback baselines.

### 2. Physics-Guided Downwind Dispersion Modeling
- Implements Pasquill-Gifford atmospheric dispersion equations to generate dynamic **downwind plume polygons** (GeoJSON RFC 7946) oriented along the downwind trajectory `(wind_direction + 180°) % 360°`.
- Dynamically scales plume length, lateral spread, and area according to incident severity (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`) and local wind velocity.

### 3. Sensitive Receptor Exposure & Triage
- Geospatially tests if critical receptors (schools, hospitals, child welfare centers) fall inside the active dispersion polygon or immediate downwind buffer.
- Calculates physical distance (Haversine in meters) and estimated plume arrival lead time (`minutes = distance / (wind_speed * 60)`).

### 4. Event-Centric Authority Routing & Lifecycle
- Calibrated priority ranking (0–100) accounting for event severity, satellite corroboration, receptor impact, and evidence confidence.
- Deterministic routing to appropriate agencies:
  - **MCD Solid Waste Flying Squad**: Open burning, garbage fires, landfill flares.
  - **DPCC Industrial Enforcement**: Smelting stacks, unauthorized industrial emissions.
  - **PWD Dust Mitigation Wing**: Construction dust, unpaved corridor particulate suspension.
- Complete lifecycle tracking: `ACTIVE` → `VERIFIED` → `ACKNOWLEDGED` → `DISPATCHED` → `RESOLVED` with recorded field outcomes.

### 5. Citizen Home Radar & Alerts
- Delivers hyper-local air quality indices for any given coordinate.
- Automatically notifies citizens if they are located **inside the active downwind plume** of an incident, providing actionable medical and protective recommendations.

### 6. Interactive Command Dashboard & Demo Simulator
- Operational Web Dashboard built with Leaflet.js, featuring dark-mode glassmorphic aesthetics, live plume polygons, and evidence breakdowns.
- **Instant Spike Simulator**: Triggers synthetic high-contrast incidents and tests downstream dispersion, receptor impact, and alert cascades during live pitches.

---

## 🏛️ System Architecture

```
VayuNetra/
├── backend/
│   ├── api/                     # FastAPI Route Controllers
│   │   ├── health.py            # System health & API endpoint discovery
│   │   ├── feed.py              # Citizen Home Radar & active plume checks
│   │   ├── report.py            # Citizen multipart reporting + AI vision
│   │   ├── municipal.py         # GeoJSON incidents & plume feature collection
│   │   ├── events.py            # Environmental event lifecycle & outcomes
│   │   └── simulate.py          # Demo & pitch simulation triggers
│   ├── models/
│   │   └── schemas.py           # Pydantic v2 schemas & GeoJSON specifications
│   ├── services/                # Core Intelligence & Computational Services
│   │   ├── dispersion.py        # Gaussian plume modeling & spatial math
│   │   ├── incident_manager.py  # Unified ticket lifecycle & state manager
│   │   ├── receptors.py         # Sensitive receptor catalog & intersection
│   │   ├── satellite.py         # NASA FIRMS thermal hotspot matching
│   │   ├── sensors.py           # CAAQMS stations, IDW, Indian AQI breakpoints
│   │   ├── vision.py            # Computer vision evidence validator
│   │   └── weather.py           # Cached Open-Meteo meteorological client
│   ├── tests/
│   │   └── test_bff.py          # End-to-end integration test suite
│   ├── app.py                   # Central FastAPI application & static mounts
│   └── config.py                # Server configuration, paths, and CORS
├── css/
│   └── styles.css               # Command center dark-mode stylesheet
├── docs/                        # Complete System Specifications & ADRs
│   ├── product-spec.md          # SIH product requirements & boundary
│   ├── architecture.md          # Multi-layer architectural design
│   ├── api.md                   # REST API contract specification
│   ├── forecasting.md           # Atmospheric dispersion & propagation
│   ├── event-detection.md       # Anomaly detection & baseline design
│   ├── computer-vision.md       # Image evidence validation architecture
│   ├── risk.md                  # Exposure scoring & priority formulas
│   └── data-sources.md          # External data feed specifications
├── js/
│   ├── app.js                   # Leaflet map controller & UI interaction
│   └── data.js                  # Client API client & fetch layer
├── index.html                   # Authority Web Dashboard
├── AGENTS.md                    # Pair-programming guidelines & rules
└── README.md                    # Project documentation
```

---

## 🔌 API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | System health check, service metadata, and API discovery |
| `GET` | `/dashboard` | Serves the Authority Command Dashboard UI |
| `GET` | `/docs` | Interactive Swagger / OpenAPI documentation |
| `GET` | `/api/v1/feed` | Citizen Home Radar (PM2.5, AQI, weather, inside-plume warning) |
| `POST`| `/api/v1/report` | Submit citizen report with photo evidence (multipart/form-data) |
| `GET` | `/api/v1/municipal/incidents` | Standard GeoJSON FeatureCollection (points + dispersion plumes) |
| `POST`| `/api/v1/simulate/spike` | Simulate incident spike (coordinates, category, wind vectors) |
| `GET` | `/api/v1/events` | List corroborated environmental events (filterable by status/severity) |
| `GET` | `/api/v1/events/{id}` | Retrieve complete Environmental Event specification object |
| `POST`| `/api/v1/events/{id}/acknowledge` | Acknowledge active incident as an on-duty officer |
| `POST`| `/api/v1/events/{id}/outcome` | Record verified field outcome and resolve incident |

---

## ⚙️ Quickstart & Local Setup

### Docker (recommended — zero local Python setup)

```bash
docker compose up --build
# or plain Docker:
docker build -t vayunetra . && docker run -p 8000:8000 vayunetra
```

Then open **http://localhost:8000/dashboard**.

### 🌐 Live Cloud Deployment (Production on Render)

The platform is permanently deployed on **Render** (Singapore Region):

- **Authority Command Dashboard**: [https://vaayunetra-authority.onrender.com/dashboard](https://vaayunetra-authority.onrender.com/dashboard)
- **Interactive OpenAPI / Swagger Docs**: [https://vaayunetra-authority.onrender.com/docs](https://vaayunetra-authority.onrender.com/docs)
- **Health Check & API Map**: [https://vaayunetra-authority.onrender.com/](https://vaayunetra-authority.onrender.com/)

> **Uptime & Keep-Alive:** The service is configured for 24/7 availability with continuous uptime monitoring on `https://vaayunetra-authority.onrender.com/` to eliminate cold starts.

### Prerequisites (non-Docker)
- Python 3.10, 3.11, 3.12, or 3.13
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/Tannuuuu/VayuNetra.git
cd VayuNetra
```

### 2. Create and Activate Virtual Environment
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install fastapi uvicorn pillow numpy shapely httpx pydantic
```

### 4. Run the Application
```bash
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access the Platform
- **Live Authority Web Dashboard**: [https://vaayunetra-authority.onrender.com/dashboard](https://vaayunetra-authority.onrender.com/dashboard) *(Local: [http://localhost:8000/dashboard](http://localhost:8000/dashboard))*
- **Live OpenAPI / Swagger Docs**: [https://vaayunetra-authority.onrender.com/docs](https://vaayunetra-authority.onrender.com/docs) *(Local: [http://localhost:8000/docs](http://localhost:8000/docs))*
- **Live Health Check & API Map**: [https://vaayunetra-authority.onrender.com/](https://vaayunetra-authority.onrender.com/) *(Local: [http://localhost:8000/](http://localhost:8000/))*

---

## 🧪 Running Automated Tests

VaayuNetra includes an end-to-end test suite verifying API health, citizen radar IDW, active plume warning detection, GeoJSON RFC 7946 compliance, computer vision validation, simulation spikes, and event lifecycle state transitions.

Execute the suite directly:
```bash
python -m backend.tests.test_bff
```

Expected output:
```text
Running BFF tests...
[PASS] test_health_endpoint
[PASS] test_citizen_feed
[PASS] test_citizen_feed_inside_plume_warning
[PASS] test_municipal_incidents_geojson
[PASS] test_simulate_spike
[PASS] test_incident_report_multipart
[PASS] test_events_lifecycle

ALL 7 TESTS PASSED SUCCESSFULLY!
```

---

## 🔬 Scientific & Claims Discipline

In accordance with the [VaayuNetra Product Specification](docs/product-spec.md):
- **Satellite Latency**: Satellite observations (NASA FIRMS / Sentinel-5P) have defined orbit revisit intervals and are not instantaneous. They are utilized for independent thermal anomaly corroboration, not sole real-time truth.
- **Evidence vs. Verdict**: Citizen photo analysis and computer vision outputs indicate *visual evidence consistency* rather than legally binding source attribution.
- **Temporal Integrity**: Baseline calculations strictly observe chronological causality. Past metrics are never computed using future timestamps relative to query time.
- **Explainable Scores**: Priority scores explicitly publish their contributing factors (severity, receptor count, persistence, evidence confidence) rather than presenting opaque numbers.

---

## 🗺️ Roadmap & Milestones

- [x] **P0 (Current MVP)**:
  - Multi-source ingestion & normalization baseline.
  - Computer vision evidence classifier for citizen reports.
  - NASA FIRMS thermal anomaly spatial correlation.
  - Gaussian downwind dispersion polygon generator with wind vectors.
  - Sensitive receptor catalog intersection with ETA modeling.
  - Authority Command Dashboard & Citizen Home Radar.
  - End-to-end BFF test suite.
- [ ] **P1 (Near-term Expansion)**:
  - Persistent PostgreSQL/PostGIS database storage with H3 indexing.
  - Direct live NASA FIRMS API ingestion pipeline.
  - Sentinel-5P tropospheric column data integration.
  - Economic corridor freight and logistics vulnerability index.
- [ ] **P2 (Advanced Intelligence)**:
  - Spatiotemporal Graph Neural Networks (ST-GNN) for learned dispersion.
  - Physics + ML ensemble forecasting over 6-hour horizons.
  - Multi-city federated environmental network.

---

## 👥 Contributors
- Tanisha Choudhary and Tarun Tanmay ~Team Syntax Sorcery
