"""
Unit tests for Spatial Exposure & Definitional Cohort Engine.
"""

from engine.spatial import (
    point_in_polygon,
    evaluate_patient_exposure_intersection,
    build_definitional_cohort_characteristics
)
from engine.scenarios import get_coimbra_scenario


def test_point_in_polygon_inside_and_outside():
    """Verify 2D ray-casting polygon intersection."""
    poly = [
        [0.0, 0.0],
        [10.0, 0.0],
        [10.0, 10.0],
        [0.0, 10.0],
        [0.0, 0.0]
    ]
    # Center is inside
    assert point_in_polygon((5.0, 5.0), poly) is True
    # Outside
    assert point_in_polygon((15.0, 15.0), poly) is False
    assert point_in_polygon((-1.0, 5.0), poly) is False


def test_coimbra_patient_exposure_intersection():
    """Verify that simulated patient coordinates correctly intersect Coimbra exposure zone."""
    scenario = get_coimbra_scenario()
    
    # Inside Coimbra Mondego reach [-8.4285, 40.2035]
    inside_eval = evaluate_patient_exposure_intersection((-8.4285, 40.2035), scenario.spatial_zone)
    assert inside_eval["intersects"] is True
    assert inside_eval["city"] == "Coimbra"
    assert inside_eval["site_id"] == "oah-site-coimbra-04"

    # Outside (e.g. 15 km away)
    outside_eval = evaluate_patient_exposure_intersection((-8.6000, 40.3500), scenario.spatial_zone)
    assert outside_eval["intersects"] is False


def test_definitional_cohort_characteristics_structure():
    """Verify that Group characteristics include spatial zone Location and recreational pathway."""
    scenario = get_coimbra_scenario()
    chars = build_definitional_cohort_characteristics(scenario.spatial_zone)
    assert len(chars) == 2

    # Characteristic 1: Location reference
    loc_char = chars[0]
    assert loc_char["valueReference"]["reference"] == "Location/oah-site-coimbra-04"
    assert loc_char["exclude"] is False

    # Characteristic 2: Recreational contact
    path_char = chars[1]
    assert path_char["valueCodeableConcept"]["coding"][0]["code"] == "recreational-contact"
    assert path_char["exclude"] is False
