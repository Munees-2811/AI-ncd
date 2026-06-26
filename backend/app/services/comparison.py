"""Report comparison — diff two assessments and classify each change as a
health improvement or a downfall. Shared by the API and the desktop app so the
logic stays consistent.

Inputs are plain dicts with keys:
  id, created_at (optional), risk_level, risk_score, health_score, bmi,
  inputs (the assessment input dict)
"""
from __future__ import annotations

# Metrics to compare: (key, label, unit, source, lower_is_better)
# source "top" = read from the prediction dict; "inputs" = from inputs sub-dict.
_METRICS = [
    ("risk_score", "Risk Score", "%", "top", True),
    ("health_score", "Health Score", "/100", "top", False),
    ("bmi", "BMI", "", "top", True),
    ("systolic_bp", "Blood Pressure", "mmHg", "inputs", True),
    ("blood_sugar", "Blood Sugar", "mg/dL", "inputs", True),
    ("cholesterol", "Cholesterol", "mg/dL", "inputs", True),
    ("weight_kg", "Weight", "kg", "inputs", True),
    ("exercise_freq", "Exercise", "days/wk", "inputs", False),
    ("sleep_hours", "Sleep", "hrs", "inputs", None),  # None => closer-to-ideal better
]

_IDEAL_SLEEP = 7.5


def _get(pred: dict, key: str, source: str):
    if source == "top":
        return pred.get(key)
    return (pred.get("inputs") or {}).get(key)


def _summary(pred: dict) -> dict:
    return {
        "id": pred.get("id"),
        "created_at": pred.get("created_at"),
        "risk_level": pred.get("risk_level"),
        "risk_score": pred.get("risk_score"),
        "health_score": pred.get("health_score"),
        "bmi": pred.get("bmi"),
    }


def compare_reports(current: dict, previous: dict) -> dict:
    """Return a structured comparison of the current vs previous report."""
    metrics = []
    for key, label, unit, source, lower_better in _METRICS:
        cur = _get(current, key, source)
        prev = _get(previous, key, source)
        if cur is None or prev is None:
            continue
        cur = round(float(cur), 1)
        prev = round(float(prev), 1)
        delta = round(cur - prev, 1)

        if delta == 0:
            direction, better = "same", None
        elif lower_better is None:  # sleep: closer to ideal is better
            direction = "up" if delta > 0 else "down"
            better = abs(cur - _IDEAL_SLEEP) < abs(prev - _IDEAL_SLEEP)
        else:
            direction = "up" if delta > 0 else "down"
            better = (delta < 0) if lower_better else (delta > 0)

        metrics.append({
            "key": key, "label": label, "unit": unit,
            "current": cur, "previous": prev, "delta": delta,
            "direction": direction, "better": better,
        })

    # Verdict driven by the headline health score (falls back to risk score).
    hs_delta = round(float(current.get("health_score", 0)) - float(previous.get("health_score", 0)), 1)
    if hs_delta > 0:
        verdict = "improved"
        summary = f"Your health score improved by {abs(hs_delta):g} points since your last assessment."
    elif hs_delta < 0:
        verdict = "declined"
        summary = f"Your health score dropped by {abs(hs_delta):g} points since your last assessment."
    else:
        verdict = "unchanged"
        summary = "Your health score is unchanged since your last assessment."

    improved = sum(1 for m in metrics if m["better"] is True)
    worsened = sum(1 for m in metrics if m["better"] is False)

    return {
        "available": True,
        "verdict": verdict,
        "summary": summary,
        "health_score_delta": hs_delta,
        "improved_count": improved,
        "worsened_count": worsened,
        "current": _summary(current),
        "previous": _summary(previous),
        "metrics": metrics,
    }
