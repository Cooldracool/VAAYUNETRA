# Citizen Computer Vision

## Objective

Validate whether a citizen-submitted image contains visual evidence
relevant to a pollution event.

## Candidate Classes

-   VISIBLE_SMOKE
-   OPEN_BURNING
-   DUST
-   FIRE
-   VEHICLE_EMISSION
-   INDUSTRIAL_EMISSION
-   NO_RELEVANT_EVIDENCE
-   UNCERTAIN

## Architecture

``` text
Citizen image
→ preprocessing
→ CV model
→ class probabilities
→ evidence object
→ event correlation
```

## MVP

Use a lightweight model appropriate to available training data.

Possible families: - MobileNet/EfficientNet, - lightweight YOLO where
object detection is required.

Do not choose a large model solely for branding.

## Output

``` json
{
  "category": "OPEN_BURNING",
  "confidence": 0.87,
  "model_version": "...",
  "visual_evidence": true
}
```

## Important Rule

CV does not prove the pollution source.

It says the image contains visual evidence consistent with a category.

## Evaluation

Measure: - precision/recall, - per-class F1, - confusion matrix, -
calibration, - false-positive rate.

Keep an UNCERTAIN outcome for low-confidence images.
