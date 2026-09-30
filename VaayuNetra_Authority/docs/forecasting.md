# Pollution Forecasting

## Objective

Estimate likely spatial/temporal propagation of an active event for +1h
to +6h.

## Inputs

-   event geometry,
-   pollutant observations,
-   wind speed/direction,
-   temperature/humidity,
-   historical patterns,
-   neighboring observations,
-   source hypothesis where available.

## MVP

Use: 1. wind-guided/advection-style propagation where physically
appropriate, 2. a strong statistical/tree/temporal baseline.

The purpose is to establish a measurable benchmark.

## P1

Evaluate: - LSTM, - ConvLSTM, - ensemble of physics + ML.

## P2

Evaluate: - ST-GNN/ST-GCN, - learned physics-guided models.

## Forecast Contract

Each horizon should contain:

``` text
horizon
timestamp
affected_geometry
predicted_intensity where supported
confidence
method/version
```

## Uncertainty

Confidence should generally decrease as horizon increases unless
evaluation proves otherwise.

Do not draw false-precision boundaries.

## Evaluation

Use: - MAE/RMSE for pollutant predictions where applicable, - spatial
overlap/error for affected regions, - horizon-wise performance, -
calibration, - lead-time usefulness.

Avoid claiming forecast accuracy without held-out evaluation.
