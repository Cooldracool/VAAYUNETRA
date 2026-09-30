# ADR-003: Hybrid Forecasting Roadmap

## Status

Accepted

## Decision

Start forecasting with a measurable baseline and physically
interpretable propagation. Introduce advanced ML only after data and
evaluation justify it.

## Roadmap

P0: - wind-guided propagation, - statistical/tree/temporal baseline.

P1: - LSTM/ConvLSTM, - physics + ML ensemble.

P2: - ST-GNN and advanced physics-guided learning.

## Rationale

Forecasting quality depends more on data quality, spatial/temporal
alignment and evaluation than on choosing the most sophisticated model.
