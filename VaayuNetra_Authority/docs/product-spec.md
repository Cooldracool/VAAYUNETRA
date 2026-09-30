VaayuNetra Product Specification

1. Product Definition

VaayuNetra is a multi-source environmental intelligence platform that
detects emerging hyper-local pollution events by combining official
monitoring, IoT sensors, citizen observations, satellite/thermal
evidence, and meteorological context.

It converts these observations into corroborated Environmental Event
objects, estimates likely source categories, forecasts event propagation
over the next 1--6 hours, assesses population and sensitive-receptor
exposure, ranks response priority, and routes actionable intelligence to
the appropriate authority.

2. Core USP

VaayuNetra does not just tell you where pollution is; it identifies
emerging pollution events, explains the evidence behind them, predicts
where they are likely to move, estimates who is likely to be exposed,
and helps authorities decide what to do next.

3. Product Boundary

VaayuNetra is: - pollution event intelligence, - environmental decision
support, - hardware-agnostic, - multi-source, - explainable, -
exposure-aware, - interoperable.

VaayuNetra is not: - an AQI-only dashboard, - a replacement for
CPCB/SPCB/SAFAR, - a sensor hardware vendor, - a generic PM2.5
forecasting project, - a guaranteed source-attribution system.

4. End-to-End Flow

OBSERVE → INGEST & NORMALIZE → GEO/TIME ALIGNMENT → LOCAL BASELINE →
EVENT DETECTION → EVIDENCE CORROBORATION → SOURCE HYPOTHESIS →
PROPAGATION FORECAST → EXPOSURE → RISK/PRIORITY → AUTHORITY ROUTING →
ALERT/RESPONSE → OUTCOME → LEARNING

5. Environmental Event

The Environmental Event is the central product object.

It should contain: - event ID, - creation/detection timestamps, -
observation window, - geometry/H3 cells, - pollutant observations, -
anomaly/severity, - confidence, - evidence, - source hypotheses, -
forecasts, - affected geometry, - exposure metrics, - priority, -
jurisdiction, - recommended action, - status, - outcome.

Lifecycle: CANDIDATE → CORROBORATED → ACTIVE → RESOLVED → OUTCOME
RECORDED

6. Data Sources

Ground/Official

CPCB/SPCB/CAAQMS provide authoritative monitoring where available.

Local/IoT

Higher-density sensor observations such as PM2.5/PM10 and available
meteorological variables.

Citizen

Geotagged reports with timestamp, image and optional description.
Citizen reports are evidence, not truth.

FIRMS

Thermal/active-fire evidence used for fire/burning context and
corroboration.

Sentinel-5P

Atmospheric composition context such as NO2, SO2 and CO. These are
atmospheric column products and should not be treated as direct ground
PM2.5.

Weather

Wind speed/direction, humidity, temperature, rainfall and other
available variables.

Population/Receptors

WorldPop and geospatial datasets such as OSM for exposure.

7. Detection

Detection should combine: - local baseline deviation, - temporal
persistence, - spatial neighborhood evidence, - source quality, -
corroborating evidence.

Start with interpretable methods such as rolling statistics/EWMA and
Isolation Forest.

8. Forecast

The forecast estimates likely propagation for +1h through +6h.

MVP: - wind-guided/advection-style propagation where appropriate, -
strong statistical/tree/temporal baseline.

Later: - LSTM/ConvLSTM, - spatiotemporal GNN, - physics + ML ensembles.

9. Source Hypothesis

Potential categories: - OPEN_BURNING - AGRICULTURAL_BURNING -
INDUSTRIAL_EMISSION - CONSTRUCTION_DUST - ROAD_TRAFFIC - FIRE - UNKNOWN

Output is probabilistic and evidence-backed.

10. Exposure

Estimate: - population in affected region, - schools, - hospitals, -
other sensitive receptors, - economic corridor impact.

11. Risk

Priority should consider: - severity, - exposure, - persistence, -
sensitive receptors, - contextual importance, - confidence.

The exact formula must be calibrated rather than treated as
scientifically final.

12. Authority Action

Routing should use: - event category, - jurisdiction, - source
hypothesis.

MVP routing can be deterministic.

13. Authority Dashboard

The dashboard is an environmental command center.

Core hierarchy: SITUATION → EVENTS → EVENT INTELLIGENCE → FORECAST →
EXPOSURE → RISK → ACTION → OUTCOME

It should contain: - situation KPIs, - interactive map, - event queue, -
event intelligence panel, - evidence, - source hypothesis, - forecast, -
exposure, - priority, - authority routing, - dispatch, - event
timeline, - analytics, - sensor/data health.

14. UX Principle

Avoid an AQI-app layout dominated by charts.

The officer should be able to understand an event in seconds: - what
happened, - why it was detected, - where it is going, - who is
affected, - what to do.

15. Claims Discipline

Never claim: - satellite data is always real-time, - Sentinel-5P
directly measures ground PM2.5, - FIRMS proves pollution, - source
attribution is always definitive, - unvalidated performance
percentages, - federated learning is operational when it is only a
prototype.
