"""
Validation Pipeline Tests: Validates all synthetic scenarios against the 6-Tier Harness.
"""

from engine.scenarios import load_scenario_and_compute, SCENARIOS
from engine.composer import compose_scenario_bundle
from validator.fhir_validator import OAHValidator
import os

CONFORMANCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "conformance"))
validator = OAHValidator(CONFORMANCE_DIR)


def test_validation_all_scenarios_pass():
    """Verify that all 3 demonstration scenarios pass all 6 tiers."""
    for s_id in SCENARIOS:
        scenario, evidence = load_scenario_and_compute(s_id)
        bundle = compose_scenario_bundle(scenario, evidence)
        report = validator.validate_bundle(bundle, scenario, evidence)

        assert report.all_passed is True, f"Scenario {s_id} failed validation!"
        for tier_key, tier in report.tiers.items():
            assert tier["passed"] is True, f"Tier {tier_key} failed in scenario {s_id}"
            for check in tier["checks"]:
                assert check["passed"] is True, f"Failed check {check['name']}: {check['message']}"


def test_validator_detects_illegal_risk_condition():
    """Verify that validator detects and fails if RiskAssessment.condition is illegally used."""
    scenario, evidence = load_scenario_and_compute("coimbra-cyanobacteria")
    bundle = compose_scenario_bundle(scenario, evidence)

    # Inject illegal condition into RiskAssessment
    for e in bundle["entry"]:
        if e["resource"]["resourceType"] == "RiskAssessment":
            e["resource"]["condition"] = {"coding": [{"system": "http://snomed.info/sct", "code": "40275004"}]}

    report = validator.validate_bundle(bundle, scenario, evidence)
    assert report.all_passed is False
    assert report.tiers["tier2_profiles"]["passed"] is False


def test_snomed_ct_terminology_manifest_resolution():
    """Verify that all scenarios map to verified, active SNOMED CT concepts in the Terminology Manifest."""
    import json
    with open(os.path.join(CONFORMANCE_DIR, "terminology_manifest.json"), "r", encoding="utf-8") as f:
        manifest = json.load(f)

    concept_map = {c["code"]: c for c in manifest["concepts"]}
    expected_codes = {
        "coimbra-cyanobacteria": "40275004",   # Contact dermatitis
        "toulouse-diptera": "416113008",        # Acute febrile illness
        "mondego-storm-surge": "69776003"       # Acute gastroenteritis
    }

    for s_id, expected_code in expected_codes.items():
        scenario, _ = load_scenario_and_compute(s_id)
        assert scenario.snomed_outcome_code == expected_code
        assert expected_code in concept_map
        assert concept_map[expected_code]["validation_status"] == "VERIFIED_ACTIVE"
        assert s_id in concept_map[expected_code]["scenarios"]
