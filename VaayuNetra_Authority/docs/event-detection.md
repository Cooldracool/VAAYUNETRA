# Event Detection

## Objective

Identify abnormal environmental conditions that may represent a
localized pollution event.

## Inputs

-   pollutant time series,
-   local baseline,
-   neighboring H3 cells,
-   weather context,
-   sensor quality,
-   supporting evidence.

## Detection Strategy

### Stage 1 --- Baseline

Estimate expected conditions by: - location, - hour, - day/season, -
available historical context.

### Stage 2 --- Anomaly

Candidate methods: - rolling z-score, - EWMA, - Isolation Forest.

Start with the simplest method that can be evaluated.

### Stage 3 --- Spatial Persistence

Require appropriate support across: - adjacent H3 cells, - nearby
sensors, - multiple observations, - time persistence.

### Stage 4 --- Event Creation

Create a CANDIDATE Environmental Event.

### Stage 5 --- Corroboration

Combine independent evidence before escalating.

## Outputs

``` text
event_id
candidate_geometry
pollutants
anomaly_score
severity
confidence
supporting_observations
```

## Avoid

-   fixed universal thresholds without calibration,
-   declaring every spike an event,
-   ignoring sensor quality,
-   claiming perfect detection.

## Evaluation

Measure: - precision, - recall, - false-alarm rate, - detection lead
time, - calibration.

Use labeled historical or carefully constructed evaluation scenarios.
