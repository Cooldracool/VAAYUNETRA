# VaayuNetra Data Sources & Acquisition Plan

## 1. Purpose

This document defines what each source contributes, how it enters the
system, and what limitations must be respected.

## 2. CPCB / SPCB / CAAQMS

### Inputs

-   PM2.5
-   PM10
-   NO2
-   SO2
-   timestamps
-   station coordinates
-   quality/status fields where available

### Uses

-   baseline construction,
-   anomaly detection,
-   model training,
-   validation,
-   event corroboration,
-   forecasting.

### Storage

Normalized observations in `observations`.

### Quality

Track: - station ID, - observation time, - ingestion time, -
pollutant, - value, - source, - quality flag.

## 3. IoT / Local Sensors

### Inputs

Typical: - PM2.5, - PM10, - temperature, - humidity, - gases if hardware
supports them.

### Uses

-   hyper-local trigger,
-   event corroboration,
-   forecasting features.

### Requirements

The system must be hardware-agnostic.

Minimum normalized schema:

``` text
sensor_id
timestamp
latitude
longitude
parameter
value
unit
quality_flag
source
```

## 4. Citizen Reports

### Inputs

-   report ID,
-   timestamp,
-   latitude,
-   longitude,
-   image,
-   description,
-   optional category.

### Processing

1.  Validate metadata.
2.  Store original image.
3.  Run CV.
4.  Produce evidence classification.
5.  Map to H3.
6.  Correlate with nearby events.

### Rule

A citizen report is evidence, not authoritative truth.

## 5. NASA FIRMS

### Role

-   active-fire/thermal context,
-   corroboration,
-   burning/fire source hypothesis.

### Rule

Thermal anomaly ≠ confirmed pollution source.

## 6. Sentinel-5P / TROPOMI

### Potential Variables

-   NO2,
-   SO2,
-   CO,
-   aerosol-related products,
-   cloud/context products.

### Role

-   regional atmospheric context,
-   spatial anomaly context,
-   source hypothesis support,
-   model features where appropriate.

### Critical Limitation

Products represent atmospheric column measurements and should not be
described as direct ground PM2.5 measurements.

## 7. Weather

### Variables

-   wind speed,
-   wind direction,
-   temperature,
-   humidity,
-   rainfall,
-   pressure,
-   visibility,
-   stability/boundary-layer variables where available.

### Sources

Prefer authoritative/validated sources such as IMD where available;
Open-Meteo/ERA5-type historical sources can support training and
consistent historical feature generation.

### Uses

-   anomaly interpretation,
-   propagation,
-   source hypothesis,
-   forecast features.

## 8. WorldPop

### Role

Population exposure.

Store a versioned population dataset and record: - source, - year, -
spatial resolution, - processing method.

## 9. OpenStreetMap

### Role

Sensitive receptors and infrastructure: - schools, - hospitals, -
roads, - industrial/POI context where appropriate.

## 10. Economic Corridor Data

Use an explicit corridor geometry and associated: - roads, - industrial
areas, - logistics nodes, - transport infrastructure.

The MVP should focus on one corridor/region.

## 11. Historical Data

Historical pollution + weather + event/outcome records support: -
baseline, - model training, - evaluation, - replay/demo scenarios.

## 12. Common Ingestion Contract

Every observation should carry:

``` text
source
source_record_id
observed_at
ingested_at
latitude/longitude or geometry
h3_cell
parameter
value
unit
quality_flag
raw_reference
```

## 13. Acquisition Rules

-   Never invent an API.
-   Record rate limits and access requirements.
-   Cache responsibly.
-   Keep source provenance.
-   Separate raw acquisition from normalized processing.
-   Build source adapters so providers can be swapped.
-   Clearly label live, historical, demo and simulated data.
