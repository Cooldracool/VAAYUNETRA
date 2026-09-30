# VaayuNetra System Architecture

## 1. Architecture

``` text
DATA SOURCES
  CPCB/SPCB | IoT | Citizen | FIRMS | Sentinel-5P | Weather | Population | OSM
        ↓
INGEST & NORMALIZE
        ↓
QUALITY + PROVENANCE
        ↓
GEO/TIME ALIGNMENT
  H3 + PostGIS + temporal resampling
        ↓
LOCAL BASELINE
        ↓
EVENT DETECTION
        ↓
EVIDENCE CORROBORATION
        ↓
SOURCE HYPOTHESIS
        ↓
FORECAST
  Physics-guided + ML
        ↓
EXPOSURE
        ↓
RISK / PRIORITY
        ↓
AUTHORITY ROUTING
        ↓
ALERT / RESPONSE
        ↓
OUTCOME
        ↓
LEARNING / MODEL IMPROVEMENT
```

## 2. Layered Architecture

### Layer 1 --- Data Sources

External feeds, APIs, sensor streams, citizen uploads and geospatial
datasets.

### Layer 2 --- Ingestion & Processing

Source adapters, validation, normalization, timestamp normalization,
coordinate validation, deduplication and spatial/temporal alignment.

### Layer 3 --- Storage

-   PostgreSQL/PostGIS for core relational/geospatial state.
-   TimescaleDB where time-series workloads justify it.
-   Object/raw storage for original files or archives where required.
-   Redis for caching/short-lived operational state where required.

### Layer 4 --- Intelligence

-   local baseline,
-   event detection,
-   evidence fusion,
-   source hypothesis,
-   propagation forecasting,
-   exposure,
-   risk.

### Layer 5 --- API/Application

FastAPI backend and frontend applications.

### Layer 6 --- Stakeholders

-   field authorities,
-   district/state authorities,
-   citizens,
-   researchers/policymakers.

## 3. Architectural Principle

Do not send all raw sources into one monolithic ML model.

Use:

``` text
Raw Sources
→ Adapters
→ Normalization
→ Alignment
→ Evidence/features
→ Specialized intelligence
→ Event fusion
→ Environmental Event
→ Forecast/Exposure/Risk
→ Action
```

## 4. Spatial Architecture

H3: - spatial indexing, - aggregation, - neighborhood lookup, - event
clustering.

PostGIS: - authoritative geometries, - spatial joins, - jurisdiction, -
corridors, - receptors, - event polygons.

## 5. Backend Services

Recommended modules: - ingestion, - processing, - detection, - fusion, -
source, - forecasting, - exposure, - risk, - alerts, - API.

These can be modular packages initially; do not force microservices
unless scaling requires them.

## 6. Frontend Architecture

Primary: - Authority Dashboard.

Secondary: - Citizen PWA.

Shared frontend model: `EnvironmentalEvent`.

The map, queue, event panel, forecast, exposure, risk and alert workflow
should consume the same event model.

## 7. Authority Dashboard Architecture

``` text
Situation Overview
      ↓
Interactive Map
      ↓
Priority Event Queue
      ↓
Selected Environmental Event
      ├─ Evidence
      ├─ Source Hypothesis
      ├─ Forecast
      ├─ Exposure
      ├─ Risk
      ├─ Authority Routing
      ├─ Recommended Action
      └─ Timeline / Outcome
```

## 8. Infrastructure

MVP: - Docker, - PostgreSQL/PostGIS, - application container(s), -
GitHub Actions.

Add Redis/background workers only when asynchronous ingestion or jobs
require them.

Kubernetes/cloud orchestration is optional and should not block the MVP.

## 9. Reliability Principles

-   Every observation has provenance.
-   Every derived event keeps evidence lineage.
-   Confidence must be distinguishable from severity.
-   Missing data should reduce confidence or be explicitly represented.
-   External feed failures should not crash the whole platform.
-   Processing should be idempotent where possible.
