# VaayuNetra Development Plan

## 1. Objective

Build a technically credible end-to-end event-intelligence MVP before
adding advanced models.

## 2. Development Order

### Phase 0 --- Repository Audit

-   inspect current repository,
-   identify existing frontend/backend/data/ML,
-   map reusable components,
-   identify architectural conflicts,
-   document missing P0 work.

### Phase 1 --- Foundation

-   Docker,
-   PostgreSQL/PostGIS,
-   project configuration,
-   migrations,
-   core types,
-   Environmental Event schema.

### Phase 2 --- Data

-   source adapter interface,
-   one working ground-data adapter,
-   normalization,
-   quality checks,
-   H3 mapping,
-   provenance.

### Phase 3 --- Detection

-   local baseline,
-   anomaly detector,
-   spatial/temporal persistence,
-   candidate event creation.

### Phase 4 --- Citizen Evidence

-   citizen report endpoint,
-   image storage,
-   CV service,
-   evidence record,
-   event correlation.

### Phase 5 --- Fusion

-   evidence scoring,
-   corroboration,
-   confidence,
-   event lifecycle.

### Phase 6 --- Weather + Forecast

-   weather adapter,
-   wind-guided propagation,
-   first forecast API,
-   +1h to +6h representation.

### Phase 7 --- Exposure + Risk

-   population intersection,
-   receptors,
-   corridor impact,
-   priority score.

### Phase 8 --- Authority Dashboard

-   dashboard shell,
-   map,
-   event queue,
-   event panel,
-   evidence,
-   forecast,
-   exposure,
-   risk,
-   routing,
-   dispatch,
-   timeline.

### Phase 9 --- External Context

-   FIRMS,
-   Sentinel-5P,
-   richer corridor context.

### Phase 10 --- Evaluation

-   detection metrics,
-   forecast metrics,
-   calibration,
-   routing,
-   latency,
-   reliability.

## 3. P0 / P1 / P2

P0: - core event loop, - dashboard, - basic ML, - one reliable data
path.

P1: - richer satellite context, - source hypothesis, - better
forecast, - interoperability.

P2: - ST-GNN, - advanced hybrid modeling, - federated learning, -
multi-city federation.

## 4. Definition of Done

A feature is complete when: - code is implemented, - relevant tests
pass, - errors are handled, - data contracts are documented, -
uncertainty/provenance is preserved, - UI behavior is coherent, - demo
mode is clearly labeled if applicable.

## 5. Development Orchestration

Claude: - architecture, - research, - ML design, - technical review, -
acceptance criteria.

Codex: - repository inspection, - implementation, - tests, -
integration, - refactoring.

Team: - final decisions, - validation, - merge.

Workflow: Goal → Claude design → implementation ticket → Codex
implementation → tests → Claude review → Codex fixes → team validation →
merge → docs update.

## 6. First Codex Task

Audit the current repository against this documentation without
modifying code.

Return: 1. repository structure, 2. existing modules, 3. existing data
models, 4. APIs, 5. ML, 6. frontend, 7. infrastructure, 8. missing P0,
9. architecture conflicts, 10. technical debt, 11. recommended
implementation order, 12. files for the first implementation task.
