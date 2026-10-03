"""
REST API & CDS Hooks Reference Server for OneAquaHealth Semantic Interoperability Bridge.
Implements:
1. Standard FHIR R4 Resource Endpoints (/api/fhir/...)
2. Documented OAH Custom Search Parameters (?oah-hazard=..., ?oah-location=...)
3. CDS Hooks Discovery & Exposure Advisory Service (/cds-services/...)
4. Full Interoperability Demonstration Runner (/api/demo/run)
5. Interactive Standards Conformance Inspector (/api/conformance)
6. Web Console Static File Serving
"""

import json
import os
import sys
import urllib.parse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from typing import Dict, Any

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.scenarios import load_scenario_and_compute, SCENARIOS
from engine.composer import compose_scenario_bundle
from engine.spatial import evaluate_patient_exposure_intersection
from validator.fhir_validator import OAHValidator

CONFORMANCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "conformance"))
WEB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web"))

validator = OAHValidator(CONFORMANCE_DIR)


class OAHServerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        # CORS preflight / headers
        if path == "/api/fhir/metadata":
            self.handle_capability_statement()
        elif path.startswith("/api/fhir/"):
            self.handle_fhir_resource(path[len("/api/fhir/"):], params)
        elif path == "/cds-services":
            self.handle_cds_discovery()
        elif path == "/api/demo/run":
            scenario_id = params.get("scenario", ["coimbra-cyanobacteria"])[0]
            self.handle_demo_run(scenario_id)
        elif path == "/api/conformance":
            self.handle_conformance()
        elif path == "/api/terminology":
            self.handle_terminology()
        elif path == "/api/scenarios":
            self.handle_scenario_list()
        else:
            # Fall back to serving static files from web/
            if path == "/" or path == "":
                self.path = "/index.html"
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            payload = json.loads(body) if body else {}
        except Exception:
            payload = {}

        if path == "/cds-services/oah-exposure-advisory":
            self.handle_cds_exposure_advisory(payload)
        elif path == "/api/demo/run":
            scenario_id = payload.get("scenario", "coimbra-cyanobacteria")
            self.handle_demo_run(scenario_id)
        else:
            self.send_error(404, "Endpoint not found")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def send_json_response(self, data: Any, status: int = 200, content_type: str = "application/json"):
        payload = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_cors_headers()
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def handle_capability_statement(self):
        cap_file = os.path.join(CONFORMANCE_DIR, "capabilitystatement.json")
        if os.path.exists(cap_file):
            with open(cap_file, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            self.send_json_response(data, content_type="application/fhir+json")
        else:
            self.send_error(500, "CapabilityStatement not found")

    def handle_scenario_list(self):
        result = []
        for s_id in SCENARIOS:
            sc, ev = load_scenario_and_compute(s_id)
            result.append({
                "id": s_id,
                "title": sc.title,
                "city": sc.city,
                "river_system": sc.river_system,
                "hazard_display": sc.hazard_display,
                "hazard_code": sc.hazard_code,
                "evidence_score": ev.score,
                "epistemic_status": ev.epistemic_status,
                "qualitative_risk": sc.qualitative_risk,
                "snomed_outcome": f"{sc.snomed_outcome_code} ({sc.snomed_outcome_display})",
                "grounding_statement": sc.grounding_statement
            })
        self.send_json_response(result)

    def handle_fhir_resource(self, resource_type: str, params: Dict[str, list]):
        scenario_id = params.get("scenario", ["coimbra-cyanobacteria"])[0]
        if scenario_id not in SCENARIOS:
            scenario_id = "coimbra-cyanobacteria"

        scenario, evidence = load_scenario_and_compute(scenario_id)
        bundle = compose_scenario_bundle(scenario, evidence)

        entries = bundle.get("entry", [])
        matched = []

        for e in entries:
            res = e.get("resource", {})
            if resource_type == "Bundle":
                matched.append(res)
            elif res.get("resourceType") == resource_type:
                # Apply OAH custom search parameters if provided
                if "oah-hazard" in params:
                    hazard_filter = params["oah-hazard"][0]
                    # Check in code or component
                    codings = res.get("code", {}).get("coding", [])
                    codes = [c.get("code") for c in codings]
                    if hazard_filter not in codes:
                        continue
                if "oah-location" in params:
                    loc_filter = params["oah-location"][0]
                    subj_ref = res.get("subject", {}).get("reference", "")
                    if loc_filter not in subj_ref:
                        continue

                matched.append(res)

        if resource_type == "Bundle":
            self.send_json_response(bundle, content_type="application/fhir+json")
        else:
            response_bundle = {
                "resourceType": "Bundle",
                "type": "searchset",
                "total": len(matched),
                "entry": [{"resource": r} for r in matched]
            }
            self.send_json_response(response_bundle, content_type="application/fhir+json")

    def handle_cds_discovery(self):
        discovery = {
            "services": [
                {
                    "hook": "patient-view",
                    "name": "OneAquaHealth Aquatic Environmental Exposure Advisory",
                    "description": "Evaluates patient authorized location context against active environmental exposure zones and surfaces non-diagnostic clinical history taking alerts.",
                    "id": "oah-exposure-advisory",
                    "prefetch": {
                        "patient": "Patient/{{context.patientId}}"
                    }
                }
            ]
        }
        self.send_json_response(discovery)

    def handle_cds_exposure_advisory(self, payload: Dict[str, Any]):
        context = payload.get("context", {})
        coords = context.get("coordinates")
        scenario_id = payload.get("scenario", "coimbra-cyanobacteria")
        scenario, evidence = load_scenario_and_compute(scenario_id)

        default_coords_map = {
            "coimbra-cyanobacteria": [-8.4285, 40.2035],
            "toulouse-diptera": [1.4355, 43.5870],
            "mondego-storm-surge": [-8.8450, 40.1510],
        }
        if not coords or not isinstance(coords, list) or len(coords) != 2:
            coords = default_coords_map.get(scenario_id, [-8.4285, 40.2035])

        intersection_result = evaluate_patient_exposure_intersection((coords[0], coords[1]), scenario.spatial_zone)

        cards = []
        if intersection_result["intersects"]:
            cards.append({
                "summary": "Environmental exposure context available",
                "indicator": "info",
                "detail": f"The patient's authorized location context intersects an active environmental exposure zone ({scenario.spatial_zone.site_name}, {scenario.city}). Recent recreational-water exposure may be relevant to clinical history taking regarding {scenario.snomed_outcome_display} (SNOMED CT {scenario.snomed_outcome_code}).",
                "source": {
                    "label": "OneAquaHealth Semantic Interoperability Bridge",
                    "url": "http://oneaquahealth.eu"
                },
                "suggestions": [
                    {
                        "label": "Inquire about recreational water contact",
                        "actions": [
                            {
                                "type": "create",
                                "description": "Document recreational aquatic exposure history in clinical notes."
                            }
                        ]
                    }
                ],
                "links": [
                    {
                        "label": f"Inspect Population RiskAssessment (FHIR R4)",
                        "url": f"http://localhost:8000/api/fhir/RiskAssessment?scenario={scenario.scenario_id}",
                        "type": "absolute"
                    },
                    {
                        "label": f"View Location GeoJSON ({scenario.city})",
                        "url": f"http://localhost:8000/api/fhir/Location?scenario={scenario.scenario_id}",
                        "type": "absolute"
                    }
                ]
            })

        self.send_json_response({"cards": cards, "intersection_evaluation": intersection_result})

    def handle_demo_run(self, scenario_id: str):
        if scenario_id not in SCENARIOS:
            scenario_id = "coimbra-cyanobacteria"

        scenario, evidence = load_scenario_and_compute(scenario_id)
        bundle = compose_scenario_bundle(scenario, evidence)
        report = validator.validate_bundle(bundle, scenario, evidence)
        rep_dict = report.to_dict()

        # Build chronological audit steps for Judge Mode live log
        steps = [
            {
                "step": 1,
                "title": "Multi-Source Evidence Ingestion",
                "detail": f"Ingested {len(scenario.citizen_reports)} citizen reports, {len(scenario.sensor_readings)} calibrated sensor telemetry readings, and {len(scenario.lab_assays)} lab assays for {scenario.city}.",
                "status": "COMPLETED"
            },
            {
                "step": 2,
                "title": "Deterministic Corroboration Scoring",
                "detail": f"Calculated sub-scores (Cs={evidence.sub_scores.sensor_corroboration}, Cc={evidence.sub_scores.citizen_agreement}, Ct={evidence.sub_scores.temporal_consistency}) yielding composite score S = {evidence.score} (Methodology v0.1 fixed weights: 0.4/0.3/0.3).",
                "status": "COMPLETED"
            },
            {
                "step": 3,
                "title": "Epistemic Status Classification",
                "detail": f"Evaluated score and laboratory evidence. Classified assertion as '{evidence.epistemic_status}' ({evidence.epistemic_display}).",
                "status": "COMPLETED"
            },
            {
                "step": 4,
                "title": "Observation Semantic Synthesis",
                "detail": f"Created Hazard Observation with ascertainment technique '{scenario.ascertainment_technique}' and epistemic extension oah-evidence-status (valueCodeableConcept). Created standalone Evidence Support Observation (focus: Hazard Obs).",
                "status": "COMPLETED"
            },
            {
                "step": 5,
                "title": "Geospatial Exposure & Definitional Cohort Computation",
                "detail": f"Computed GIS buffer and boundary for {scenario.spatial_zone.site_name}. Represented definitional exposed population as FHIR Group (actual=false) with criteria.",
                "status": "COMPLETED"
            },
            {
                "step": 6,
                "title": "Population-Level Risk Assessment",
                "detail": f"Assembled FHIR RiskAssessment: subject=Group, basis=Evidence Support Observation, method=oah-environmental-exposure-assessment, prediction.outcome=SNOMED CT {scenario.snomed_outcome_code} ({scenario.snomed_outcome_display}), qualitativeRisk={scenario.qualitative_risk}.",
                "status": "COMPLETED"
            },
            {
                "step": 7,
                "title": "Provenance & Operational Workflow Dispatch",
                "detail": f"Recorded FHIR Provenance audit trail. Dispatched operational FHIR Flag (surveillance alert) and CommunicationRequest (field inspection ticket).",
                "status": "COMPLETED"
            },
            {
                "step": 8,
                "title": "6-Tier Standards Conformance Verification",
                "detail": f"Ran automated validation harness. {rep_dict['summary']['passed_checks']}/{rep_dict['summary']['total_checks']} checks passed across all 6 tiers.",
                "status": "PASSED" if report.all_passed else "FAILED"
            }
        ]

        clinical_profiles = {
            "coimbra-cyanobacteria": {
                "facility": "Hospital Pediátrico de Coimbra • Emergency Department",
                "bay": "Bay 03 • Encounter #ENC-9281",
                "patient_name": "Maria Silva, 14 yo female",
                "triage": "Urgency 2 (Yellow) • HR: 112 bpm • T: 38.2°C",
                "reason": "Patient reports acute pruritic erythematous rash on limbs and torso following recreational freshwater immersion.",
                "location_context": "40.2033° N, -8.4285° W (Intersects Monitored Reach #4)",
                "snomed_outcome": "SNOMED CT 40275004 (Contact dermatitis)",
                "clinical_consideration": "Consider freshwater microcystin contact dermatitis in differential diagnosis vs. standard atopic etiology. Inquire regarding recreational immersion duration and visible scum.",
                "doc_text": "Patient confirmed recreational water contact at Mondego Reach #4 within last 24h during active Cyanobacteria surveillance alert. Environmental history documented in clinical encounter notes.",
                "dispatch_id": f"CommunicationRequest/oah-comm-{scenario.scenario_id}",
                "dispatch_target": "Municipal Water Inspection Unit (Coimbra)",
                "dispatch_action": "Pontoon Cautionary Signage & Reference Grab Testing",
                "dossier_ref": "ECDC/OAH-2026-PT04"
            },
            "toulouse-diptera": {
                "facility": "Centre Hospitalier Universitaire de Toulouse (CHU Purpan) • Triage",
                "bay": "Cubicle 07 • Encounter #ENC-4418",
                "patient_name": "Lucas Bernard, 28 yo male",
                "triage": "Urgency 3 (Green) • HR: 88 bpm • T: 38.9°C",
                "reason": "Patient presents with acute febrile syndrome, localized lymphadenopathy, and multiple erythematous insect bites sustained during evening run along riparian park margins.",
                "location_context": "43.5875° N, 1.4345° E (Intersects Île du Ramier Zone)",
                "snomed_outcome": "SNOMED CT 416113008 (Preferred term: Disorder characterized by fever | Display: Acute febrile illness)",
                "clinical_consideration": "Evaluate acute febrile illness (SNOMED CT 416113008) in context of documented Diptera vector surge in riparian zone. Inquire about outdoor mosquito bites and duration of exposure.",
                "doc_text": "Patient confirmed high-density mosquito bite exposure in Île du Ramier riparian corridor during active Diptera vector alert. Vector exposure history documented in EHR.",
                "dispatch_id": f"CommunicationRequest/oah-comm-{scenario.scenario_id}",
                "dispatch_target": "Service Communal d'Hygiène et de Santé (SCHS Toulouse)",
                "dispatch_action": "Biological Vector Larvicide Treatment & Riparian Drainage Clearing",
                "dossier_ref": "ECDC/OAH-2026-FR02"
            },
            "mondego-storm-surge": {
                "facility": "Hospital Distrital da Figueira da Foz • Emergency Ward",
                "bay": "Bay 01 • Encounter #ENC-7703",
                "patient_name": "João Ferreira, 34 yo male",
                "triage": "Urgency 2 (Yellow) • HR: 104 bpm • T: 38.6°C",
                "reason": "Patient reports sudden onset watery diarrhea, severe crampy abdominal pain, and nausea 18 hours after windsurfing in lower estuary reaches.",
                "location_context": "40.1510° N, -8.8450° W (Intersects Estuary Transition Reach)",
                "snomed_outcome": "SNOMED CT 69776003 (Acute gastroenteritis)",
                "clinical_consideration": "Incorporate confirmed enteropathogen (E. coli >2400 CFU/100mL) storm surge contamination into clinical history taking for acute gastroenteritis (SNOMED CT 69776003).",
                "doc_text": "Patient confirmed recreational water inhalation/ingestion during windsurfing in Mondego Estuary reach during storm surge runoff alert. Enteropathogen exposure documented in EHR.",
                "dispatch_id": f"CommunicationRequest/oah-comm-{scenario.scenario_id}",
                "dispatch_target": "Administração Regional de Saúde (ARS Centro / APA)",
                "dispatch_action": "Immediate Recreational Bathing Water Closure & Microbial Resampling",
                "dossier_ref": "ECDC/OAH-2026-PT09"
            }
        }

        self.send_json_response({
            "scenario": {
                "id": scenario.scenario_id,
                "title": scenario.title,
                "city": scenario.city,
                "river_system": scenario.river_system,
                "site_id": scenario.spatial_zone.site_id,
                "site_name": scenario.spatial_zone.site_name,
                "grounding_statement": scenario.grounding_statement,
                "hazard_code": scenario.hazard_code,
                "hazard_display": scenario.hazard_display,
                "evidence_score": evidence.score,
                "epistemic_status": evidence.epistemic_status,
                "epistemic_display": evidence.epistemic_display,
                "sub_scores": {
                    "sensor_corroboration": evidence.sub_scores.sensor_corroboration,
                    "citizen_agreement": evidence.sub_scores.citizen_agreement,
                    "temporal_consistency": evidence.sub_scores.temporal_consistency
                },
                "estimated_exposed_population": scenario.spatial_zone.estimated_exposed_population,
                "buffer_meters": scenario.spatial_zone.buffer_meters,
                "recreational_use_category": scenario.spatial_zone.recreational_use_category,
                "qualitative_risk": scenario.qualitative_risk,
                "risk_summary": scenario.risk_summary,
                "ascertainment_technique": scenario.ascertainment_technique,
                "ascertainment_display": scenario.ascertainment_display,
                "snomed_outcome_code": scenario.snomed_outcome_code,
                "snomed_outcome_display": scenario.snomed_outcome_display,
                "snomed_preferred_term": scenario.snomed_preferred_term,
                "snomed_outcome": f"{scenario.snomed_outcome_code} | Preferred term: {scenario.snomed_preferred_term} | Display: {scenario.snomed_outcome_display}",
                "sensor_readings": [
                    {
                        "id": r.reading_id,
                        "parameter": r.parameter,
                        "value": r.value,
                        "unit": r.unit,
                        "baseline": r.nominal_baseline,
                        "exceeded": r.threshold_exceeded
                    }
                    for r in scenario.sensor_readings
                ],
                "citizen_reports": [
                    {
                        "id": c.report_id,
                        "sighting": c.sighting_type,
                        "severity": c.severity_rating,
                        "description": c.description,
                        "observer": c.observer_type
                    }
                    for c in scenario.citizen_reports
                ],
                "lab_assays": [
                    {
                        "id": a.sample_id,
                        "analyte": a.analyte,
                        "concentration": a.concentration,
                        "unit": a.unit,
                        "threshold": a.regulatory_threshold,
                        "laboratory": a.laboratory_name,
                        "confirmed": a.confirmed_positive
                    }
                    for a in scenario.lab_assays
                ],
                "clinical_encounter": clinical_profiles.get(scenario.scenario_id, clinical_profiles["coimbra-cyanobacteria"])
            },
            "steps": steps,
            "validation_report": rep_dict,
            "bundle": bundle
        })

    def handle_conformance(self):
        items = []
        for root, dirs, files in os.walk(CONFORMANCE_DIR):
            for f in files:
                if f.endswith(".json"):
                    with open(os.path.join(root, f), "r", encoding="utf-8") as fp:
                        data = json.load(fp)
                        items.append({
                            "resourceType": data.get("resourceType"),
                            "id": data.get("id"),
                            "url": data.get("url"),
                            "title": data.get("title") or data.get("name"),
                            "status": data.get("status"),
                            "version": data.get("version"),
                            "description": data.get("description"),
                            "raw": data
                        })
        self.send_json_response({"total": len(items), "items": items})

    def handle_terminology(self):
        term_file = os.path.join(CONFORMANCE_DIR, "terminology_manifest.json")
        if os.path.exists(term_file):
            with open(term_file, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            self.send_json_response(data)
        else:
            self.send_error(404, "Terminology manifest not found")


def run_server(port: int = 8000):
    server_address = ("", port)
    httpd = ThreadingHTTPServer(server_address, OAHServerHandler)
    print(f"OAH-Bridge FHIR R4 & CDS Server running on port {port}...")
    httpd.serve_forever()


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port)
