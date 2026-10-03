"""
Unit tests for Deterministic Evidence Support Scoring & Epistemic Classification.
"""

import pytest
from engine.scoring import (
    WEIGHT_SENSOR,
    WEIGHT_CITIZEN,
    WEIGHT_TEMPORAL,
    compute_composite_evidence,
    EvidenceSubScores
)
from engine.models import LabAssay


def test_fixed_weights_sum_to_one():
    """Verify that prototype weights are fixed and sum to 1.00."""
    assert WEIGHT_SENSOR == 0.40
    assert WEIGHT_CITIZEN == 0.30
    assert WEIGHT_TEMPORAL == 0.30
    assert pytest.approx(WEIGHT_SENSOR + WEIGHT_CITIZEN + WEIGHT_TEMPORAL, 0.001) == 1.00


def test_coimbra_score_calibration():
    """Verify exact 0.86 evidence score for Coimbra calibration values."""
    sub_scores = EvidenceSubScores(
        sensor_corroboration=0.90,
        citizen_agreement=0.75,
        temporal_consistency=0.92
    )
    result = compute_composite_evidence(sub_scores=sub_scores)
    assert result.score == 0.86
    assert result.epistemic_status == "inferred"
    assert "Modeled Inference" in result.epistemic_display
    assert result.methodology_version == "v0.1-prototype"
    assert "Not clinically validated" in result.disclaimer


def test_laboratory_confirmation_override():
    """Verify that a positive wet-lab assay overrides inference to confirmed."""
    sub_scores = EvidenceSubScores(
        sensor_corroboration=0.85,
        citizen_agreement=0.70,
        temporal_consistency=0.88
    )
    lab_assays = [
        LabAssay(
            sample_id="lab-01",
            timestamp="2026-10-02T10:00:00Z",
            site_id="site-01",
            analyte="Microcystin-LR",
            concentration=15.0,
            unit="ug/L",
            regulatory_threshold=1.0,
            confirmed_positive=True,
            laboratory_name="Certified Lab"
        )
    ]
    result = compute_composite_evidence(sub_scores=sub_scores, lab_assays=lab_assays)
    assert result.score == 0.81
    assert result.epistemic_status == "confirmed"
    assert result.is_lab_confirmed is True


def test_low_score_epistemic_classification():
    """Verify that low corroboration is classified as observed/low multi-source support."""
    sub_scores = EvidenceSubScores(
        sensor_corroboration=0.20,
        citizen_agreement=0.30,
        temporal_consistency=0.20
    )
    result = compute_composite_evidence(sub_scores=sub_scores)
    # S = 0.40(0.2) + 0.30(0.3) + 0.30(0.2) = 0.08 + 0.09 + 0.06 = 0.23
    assert result.score == 0.23
    assert result.epistemic_status == "observed"
