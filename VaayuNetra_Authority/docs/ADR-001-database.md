# ADR-001: PostgreSQL + PostGIS

## Status

Accepted

## Decision

Use PostgreSQL as the primary relational database and PostGIS for
geospatial operations.

TimescaleDB may be added where time-series performance requires it.

## Rationale

VaayuNetra needs: - relational event state, - geospatial joins, - H3
integration, - sensor observations, - event/evidence relationships, -
receptor intersection, - jurisdiction/corridor queries.

A single PostgreSQL/PostGIS foundation reduces unnecessary
infrastructure during the MVP.

## Consequence

Do not introduce a separate geospatial database unless profiling
demonstrates a real requirement.
