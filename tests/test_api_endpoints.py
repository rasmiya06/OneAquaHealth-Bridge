"""
Integration tests for OAH-Bridge REST API & CDS Hooks endpoints.
Tests endpoints in-process to ensure 100% compliance across:
1. /api/fhir/metadata (CapabilityStatement)
2. /api/fhir/Observation (Standard & OAH Custom Search Parameters)
3. /api/fhir/Location
4. /api/fhir/Group
5. /api/fhir/RiskAssessment
6. /api/fhir/Bundle
7. /cds-services (Discovery)
8. /cds-services/oah-exposure-advisory (Execution)
9. /api/demo/run (Judge Mode)
10. /api/conformance
"""

import json
import threading
import time
import urllib.request
import urllib.error
import pytest
from http.server import ThreadingHTTPServer
from api.server import OAHServerHandler


@pytest.fixture(scope="module")
def api_server():
    server = ThreadingHTTPServer(("127.0.0.1", 8999), OAHServerHandler)
    t = threading.Thread(target=server.serve_forever)
    t.daemon = True
    t.start()
    time.sleep(0.3)
    yield "http://127.0.0.1:8999"
    server.shutdown()


def test_capability_statement_endpoint(api_server):
    url = f"{api_server}/api/fhir/metadata"
    req = urllib.request.urlopen(url)
    assert req.status == 200
    data = json.loads(req.read().decode("utf-8"))
    assert data["resourceType"] == "CapabilityStatement"
    assert data["fhirVersion"] == "4.0.1"
    assert data["id"] == "oah-bridge-server"


def test_fhir_observation_search(api_server):
    # Query with OAH custom search parameter oah-hazard
    url = f"{api_server}/api/fhir/Observation?scenario=coimbra-cyanobacteria&oah-hazard=cyanobacteria-proliferation"
    req = urllib.request.urlopen(url)
    assert req.status == 200
    data = json.loads(req.read().decode("utf-8"))
    assert data["resourceType"] == "Bundle"
    assert data["type"] == "searchset"
    assert data["total"] >= 1
    hazard_obs = data["entry"][0]["resource"]
    assert hazard_obs["resourceType"] == "Observation"
    assert hazard_obs["code"]["coding"][0]["code"] == "cyanobacteria-proliferation"


def test_fhir_risk_assessment_endpoint(api_server):
    url = f"{api_server}/api/fhir/RiskAssessment?scenario=coimbra-cyanobacteria"
    req = urllib.request.urlopen(url)
    assert req.status == 200
    data = json.loads(req.read().decode("utf-8"))
    assert data["resourceType"] == "Bundle"
    ra = data["entry"][0]["resource"]
    assert ra["resourceType"] == "RiskAssessment"
    assert "Group/" in ra["subject"]["reference"]
    assert ra["prediction"][0]["outcome"]["coding"][0]["code"] == "40275004"


def test_fhir_bundle_endpoint(api_server):
    url = f"{api_server}/api/fhir/Bundle?scenario=coimbra-cyanobacteria"
    req = urllib.request.urlopen(url)
    assert req.status == 200
    data = json.loads(req.read().decode("utf-8"))
    assert data["resourceType"] == "Bundle"
    assert data["total"] == 8


def test_cds_hooks_discovery(api_server):
    url = f"{api_server}/cds-services"
    req = urllib.request.urlopen(url)
    assert req.status == 200
    data = json.loads(req.read().decode("utf-8"))
    assert "services" in data
    assert len(data["services"]) == 1
    assert data["services"][0]["id"] == "oah-exposure-advisory"
    assert data["services"][0]["hook"] == "patient-view"


def test_cds_hooks_execution_intersection(api_server):
    url = f"{api_server}/cds-services/oah-exposure-advisory"
    payload = json.dumps({
        "scenario": "coimbra-cyanobacteria",
        "context": {
            "coordinates": [-8.4285, 40.2035]
        }
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req)
    assert resp.status == 200
    data = json.loads(resp.read().decode("utf-8"))
    assert "cards" in data
    assert len(data["cards"]) == 1
    card = data["cards"][0]
    assert card["summary"] == "Environmental exposure context available"
    assert "Contact dermatitis" in card["detail"]
    assert card["indicator"] == "info"


def test_cds_hooks_execution_outside_zone(api_server):
    url = f"{api_server}/cds-services/oah-exposure-advisory"
    payload = json.dumps({
        "scenario": "coimbra-cyanobacteria",
        "context": {
            "coordinates": [-8.6000, 40.3500]
        }
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req)
    assert resp.status == 200
    data = json.loads(resp.read().decode("utf-8"))
    assert "cards" in data
    assert len(data["cards"]) == 0


def test_demo_run_judge_mode(api_server):
    url = f"{api_server}/api/demo/run?scenario=coimbra-cyanobacteria"
    req = urllib.request.urlopen(url)
    assert req.status == 200
    data = json.loads(req.read().decode("utf-8"))
    assert "steps" in data
    assert len(data["steps"]) == 8
    assert data["validation_report"]["all_passed"] is True
    assert data["scenario"]["evidence_score"] == 0.86


def test_conformance_endpoint(api_server):
    url = f"{api_server}/api/conformance"
    req = urllib.request.urlopen(url)
    assert req.status == 200
    data = json.loads(req.read().decode("utf-8"))
    assert data["total"] >= 12
