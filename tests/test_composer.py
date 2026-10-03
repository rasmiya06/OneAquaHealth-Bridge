"""
Unit tests for FHIR R4 Resource Composer.
"""

from engine.scenarios import load_scenario_and_compute
from engine.composer import compose_scenario_bundle


def test_bundle_composition_resource_types():
    """Verify that compose_scenario_bundle creates all 8 expected FHIR resources."""
    scenario, evidence = load_scenario_and_compute("coimbra-cyanobacteria")
    bundle = compose_scenario_bundle(scenario, evidence)

    assert bundle["resourceType"] == "Bundle"
    assert bundle["type"] == "collection"
    assert bundle["total"] == 8

    rtypes = {e["resource"]["resourceType"] for e in bundle["entry"]}
    expected_types = {"Location", "Observation", "Group", "RiskAssessment", "Provenance", "Flag", "CommunicationRequest"}
    assert expected_types == rtypes


def test_hazard_observation_semantics():
    """Verify Observation.method ascertainment technique vs epistemic extension."""
    scenario, evidence = load_scenario_and_compute("coimbra-cyanobacteria")
    bundle = compose_scenario_bundle(scenario, evidence)

    hazard_obs = [
        e["resource"] for e in bundle["entry"]
        if e["resource"]["resourceType"] == "Observation" and e["resource"]["code"]["coding"][0]["code"] != "evidence-support-score"
    ][0]

    # Observation.method must be ascertainment technique
    assert hazard_obs["method"]["coding"][0]["system"] == "http://oneaquahealth.eu/fhir/cs/observation-technique"
    assert hazard_obs["method"]["coding"][0]["code"] == "in-situ-sensor-probe"

    # Epistemic status must be carried by extension with valueCodeableConcept
    ext = [e for e in hazard_obs["extension"] if "oah-evidence-status" in e["url"]][0]
    assert "valueCodeableConcept" in ext
    assert ext["valueCodeableConcept"]["coding"][0]["system"] == "http://oneaquahealth.eu/fhir/cs/evidence-status"
    assert ext["valueCodeableConcept"]["coding"][0]["code"] == "inferred"


def test_evidence_support_observation_semantics():
    """Verify standalone Evidence Support Observation with focus and components."""
    scenario, evidence = load_scenario_and_compute("coimbra-cyanobacteria")
    bundle = compose_scenario_bundle(scenario, evidence)

    ev_obs = [
        e["resource"] for e in bundle["entry"]
        if e["resource"]["resourceType"] == "Observation" and e["resource"]["code"]["coding"][0]["code"] == "evidence-support-score"
    ][0]

    assert ev_obs["valueDecimal"] == 0.86
    assert len(ev_obs["focus"]) == 1
    assert "Observation/oah-hazard-coimbra-cyanobacteria" in ev_obs["focus"][0]["reference"]
    assert len(ev_obs["component"]) == 3


def test_risk_assessment_semantics():
    """Verify RiskAssessment.subject is Group and prediction.outcome is SNOMED CT."""
    scenario, evidence = load_scenario_and_compute("coimbra-cyanobacteria")
    bundle = compose_scenario_bundle(scenario, evidence)

    ra = [e["resource"] for e in bundle["entry"] if e["resource"]["resourceType"] == "RiskAssessment"][0]

    # Subject must be definitional Group
    assert "Group/" in ra["subject"]["reference"]

    # Basis must reference Evidence Support Observation
    basis_refs = [b["reference"] for b in ra["basis"]]
    assert any("oah-evidence-support" in r for r in basis_refs)

    # Condition must NOT be present
    assert "condition" not in ra

    # Method must be explicit
    assert ra["method"]["coding"][0]["code"] == "oah-environmental-exposure-assessment"

    # Prediction outcome must be SNOMED CT 40275004
    pred = ra["prediction"][0]
    assert pred["outcome"]["coding"][0]["system"] == "http://snomed.info/sct"
    assert pred["outcome"]["coding"][0]["code"] == "40275004"
    assert pred["qualitativeRisk"]["coding"][0]["code"] == "moderate"
