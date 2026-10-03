"""
Unit tests for CDS Hooks Protocol & Exposure Advisory Evaluation.
"""

from engine.scenarios import load_scenario_and_compute
from engine.spatial import evaluate_patient_exposure_intersection


def test_cds_service_exposure_intersection():
    """Verify CDS service correctly generates positive card when patient intersects zone."""
    scenario, _ = load_scenario_and_compute("coimbra-cyanobacteria")
    
    # Patient coordinates inside Mondego Reach
    inside_coords = (-8.4285, 40.2035)
    res = evaluate_patient_exposure_intersection(inside_coords, scenario.spatial_zone)
    assert res["intersects"] is True

    # Card content evaluation
    expected_summary = "Environmental exposure context available"
    expected_snomen = "Contact dermatitis"
    assert res["city"] == "Coimbra"


def test_cds_service_outside_exposure_zone():
    """Verify CDS service returns non-intersecting result when patient is far outside zone."""
    scenario, _ = load_scenario_and_compute("coimbra-cyanobacteria")
    
    outside_coords = (-8.5500, 40.3500)
    res = evaluate_patient_exposure_intersection(outside_coords, scenario.spatial_zone)
    assert res["intersects"] is False
