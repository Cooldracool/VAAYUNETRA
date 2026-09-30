# Exposure & Risk Engine

## Objective

Prioritize environmental events according to severity, exposure and
actionability.

## Exposure Inputs

-   forecast affected geometry,
-   population grid,
-   schools,
-   hospitals,
-   other sensitive receptors,
-   economic corridor assets,
-   persistence/duration.

## Exposure Outputs

``` text
population_exposed
schools_affected
hospitals_affected
other_receptors
corridor_impact
```

## Priority

Conceptually:

``` text
Priority ≈
severity
× exposure
× persistence
× contextual sensitivity
× confidence
```

The exact formula must be calibrated.

## Why Confidence Matters

A severe event supported by weak evidence should not necessarily outrank
a similarly severe event supported by strong independent evidence.

## Explainability

The API and dashboard should expose score components: - severity
contribution, - exposure contribution, - sensitive-site contribution, -
persistence, - confidence.

## Authority Routing

MVP routing is deterministic:

``` text
event category + jurisdiction → authority
```

Potential categories: - municipal, - agriculture, -
SPCB/environmental, - fire, - transport/traffic, - district
administration.

## Evaluation

Measure: - ranking usefulness, - routing accuracy, - exposure estimation
error, - response lead time where outcome data exists.

Do not claim that the priority score is scientifically optimal until
evaluated.
