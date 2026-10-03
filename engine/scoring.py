"""
Deterministic Evidence Support Scoring & Epistemic Classification Engine.
Version: v0.1-prototype

Methodology:
S = w_sensor * C_sensor + w_citizen * C_citizen + w_temporal * C_temporal
Weights: w_sensor = 0.40, w_citizen = 0.30, w_temporal = 0.30 (Sum = 1.00)

Disclaimer:
These weights are prototype assumptions for demonstration and are not clinically validated.
"""

from typing import List, Optional
from engine.models import (
    CitizenReport,
    SensorReading,
    LabAssay,
    ModelInference,
    EvidenceSubScores,
    CompositeEvidenceResult
)

# Frozen prototype weights v0.1
WEIGHT_SENSOR = 0.40
WEIGHT_CITIZEN = 0.30
WEIGHT_TEMPORAL = 0.30

# Epistemic classification thresholds
THRESHOLD_STRONG_INFERRED = 0.70
THRESHOLD_MODERATE_INFERRED = 0.40


def calculate_sensor_corroboration(readings: List[SensorReading]) -> float:
    """
    Computes normalized corroboration among sensor readings.
    Evaluates the fraction of parameters that exceed anomaly thresholds.
    """
    if not readings:
        return 0.0
    exceeded_count = sum(1 for r in readings if r.threshold_exceeded)
    # Ratio of anomalous readings scaled to 0.0 - 1.0
    ratio = exceeded_count / len(readings)
    # Cap between 0.00 and 1.00
    return round(min(1.0, max(0.0, ratio * 0.95 + 0.05 if exceeded_count > 0 else 0.0)), 2)


def calculate_citizen_agreement(reports: List[CitizenReport]) -> float:
    """
    Computes citizen consensus and report density index.
    Based on report count and average severity rating (1-5).
    """
    if not reports:
        return 0.0
    avg_severity = sum(r.severity_rating for r in reports) / len(reports)
    # Scale severity 1-5 to 0.2 - 1.0
    severity_norm = avg_severity / 5.0
    # Density factor (saturates at 5 reports)
    density_factor = min(1.0, len(reports) / 4.0)
    score = (severity_norm * 0.7) + (density_factor * 0.3)
    return round(min(1.0, max(0.0, score)), 2)


def calculate_temporal_consistency(readings: List[SensorReading], reports: List[CitizenReport]) -> float:
    """
    Evaluates trend persistence over the observation window.
    High score indicates multiple timestamps showing persistent anomaly.
    """
    total_events = len(readings) + len(reports)
    if total_events == 0:
        return 0.0
    # Distinct timestamps represent temporal persistence
    all_timestamps = {r.timestamp[:13] for r in readings} | {c.timestamp[:13] for c in reports}
    time_spread = min(1.0, len(all_timestamps) / 3.0)
    consistency = 0.85 if time_spread >= 0.6 else 0.50
    return round(consistency, 2)


def compute_composite_evidence(
    sub_scores: Optional[EvidenceSubScores] = None,
    readings: Optional[List[SensorReading]] = None,
    reports: Optional[List[CitizenReport]] = None,
    lab_assays: Optional[List[LabAssay]] = None
) -> CompositeEvidenceResult:
    """
    Executes the deterministic evidence fusion algorithm.
    """
    if sub_scores is None:
        c_sensor = calculate_sensor_corroboration(readings or [])
        c_citizen = calculate_citizen_agreement(reports or [])
        c_temporal = calculate_temporal_consistency(readings or [], reports or [])
        sub_scores = EvidenceSubScores(
            sensor_corroboration=c_sensor,
            citizen_agreement=c_citizen,
            temporal_consistency=c_temporal
        )

    # Formula: S = 0.40 * Cs + 0.30 * Cc + 0.30 * Ct
    raw_score = (
        (WEIGHT_SENSOR * sub_scores.sensor_corroboration) +
        (WEIGHT_CITIZEN * sub_scores.citizen_agreement) +
        (WEIGHT_TEMPORAL * sub_scores.temporal_consistency)
    )
    score = round(raw_score, 2)

    # Check for laboratory confirmation override
    has_lab_positive = False
    if lab_assays:
        has_lab_positive = any(a.confirmed_positive for a in lab_assays)

    if has_lab_positive:
        epistemic_status = "confirmed"
        epistemic_display = "Laboratory Confirmed"
    elif score >= THRESHOLD_STRONG_INFERRED:
        epistemic_status = "inferred"
        epistemic_display = "Modeled Inference (Strong Multi-Source Support)"
    elif score >= THRESHOLD_MODERATE_INFERRED:
        epistemic_status = "inferred"
        epistemic_display = "Modeled Inference (Moderate Support)"
    else:
        epistemic_status = "observed"
        epistemic_display = "Direct Empirical Observation (Low Corroboration)"

    return CompositeEvidenceResult(
        score=score,
        methodology_version="v0.1-prototype",
        weights={
            "sensor": WEIGHT_SENSOR,
            "citizen": WEIGHT_CITIZEN,
            "temporal": WEIGHT_TEMPORAL
        },
        sub_scores=sub_scores,
        epistemic_status=epistemic_status,
        epistemic_display=epistemic_display,
        is_lab_confirmed=has_lab_positive
    )
