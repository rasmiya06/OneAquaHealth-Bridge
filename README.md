# OneAquaHealth Semantic Interoperability Bridge (OAH-Bridge)

[![Track 7: Standards & Interoperability](https://img.shields.io/badge/Hackathon-Track%207%20Standards%20%26%20Interoperability-blue.svg)](http://oneaquahealth.eu)
[![HL7 FHIR R4](https://img.shields.io/badge/HL7%C2%AE%20FHIR%C2%AE-R4%20(v4.0.1)-firebrick.svg)](conformance/)
[![CDS Hooks 1.0](https://img.shields.io/badge/CDS%20Hooks-1.0%20Reference-darkgreen.svg)](api/server.py)
[![Test Suite](https://img.shields.io/badge/Automated%20Tests-25%2F25%20PASS%20(100%25)-success.svg)](tests/)
[![Prototype Conformance](https://img.shields.io/badge/Prototype%20Audit-44%2F44%20Checks%20Passed-purple.svg)](validator/)
[![Privacy-Preserving Cohort](https://img.shields.io/badge/Cohort-Definitional%20Group%20(actual%3Dfalse)-teal.svg)](#-definitional-cohorts--privacy-architecture)

> **Official Demonstration for OneAquaHealth Hackathon — Track 7: Standards & Interoperability**  
> *Connecting environmental surveillance (sensors, citizen science, AI models) with hospital clinical awareness (HL7® FHIR® R4, CDS Hooks 1.0, SNOMED CT) to protect community health.*
>
> ⚠️ **DEMONSTRATION DATA NOTICE**: *Synthetic demonstration scenarios grounded in OneAquaHealth research-city geography (Coimbra, Toulouse, Figueira da Foz). Not live public-health surveillance.*

---

## ⚡ Executive Summary

Urban aquatic ecosystems are increasingly monitored by high-tech sensors, citizen scientists, and AI models. Yet, **when an environmental pathogen strikes, hospital emergency rooms are completely blind to it.**

A child swims in an active river bloom, presents to the ER with acute dermatitis, and the clinician evaluates ordinary atopic dermatitis or allergies without knowing about local toxic water conditions.

**OAH-Bridge** is a semantic interoperability layer that transforms multi-source environmental evidence into provenance-aware, spatially contextualized FHIR R4 health signals. Its Semantic Decision Layer explicitly represents evidence status, corroboration, exposure pathways and potentially exposed populations before connecting them to standardized clinical concepts and non-diagnostic public-health workflows:
1. **Multi-Source Evidence**: Ingests heterogeneous environmental inputs (in-situ sondes, citizen science reports, predictive models, certified wet-lab assays).
2. **Deterministic Corroboration**: Computes a transparent composite score ($S = 0.40 C_s + 0.30 C_c + 0.30 C_t$) and assigns a formal **epistemic status** (`observed`, `inferred`, `confirmed`).
3. **Spatial Exposure Geometry**: Projects GIS buffer boundaries into a definitional cohort via **FHIR `Group (actual = false)`**; individual membership is not required for the environmental exposure definition.
4. **Health Risk Context**: Evaluates population exposure risk via **FHIR `RiskAssessment`** with verified active SNOMED CT concepts and HL7 `risk-probability`.
5. **Standards-Based Workflows**: Emits validated **HL7® FHIR® R4 Bundles** with Provenance, dispatches municipal public health notices (`CommunicationRequest`), and surfaces informational **CDS Hooks 1.0** context cards (`patient-view`) during EHR triage (no diagnosis or treatment recommendation).

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph HeterogeneousInputs [1. Heterogeneous Environmental Inputs]
        Sensors["In-situ Multiparameter Sonde<br/>(Chlorophyll-a, pH, Temp, DO)"]
        Citizen["Citizen Science Mobile App<br/>(Geotagged Sighting + Photographic Scum)"]
        Models["Predictive Ecological Models<br/>(DipteraCAST / Satellite Bloom Inference)"]
        Labs["Certified Wet-Lab Assays<br/>(HPLC-MS Cyanotoxin / Grab Samples)"]
    end

    subgraph DecisionEngine [2. OAH Semantic Decision Layer - SLS]
        Ingest["Evidence Ingestion & Normalization"]
        Score["Corroboration Scorer<br/>S = 0.40*Cs + 0.30*Cc + 0.30*Ct"]
        Epistemic["Epistemic Classifier<br/>(observed -> inferred -> confirmed)"]
        Spatial["Spatial Intersection Engine<br/>(Raycasting Point-in-Polygon Buffer)"]
    end

    subgraph FHIRSuite [3. HL7® FHIR® R4 Knowledge Graph]
        CS["7 Canonical CodeSystems"]
        VS["6 ValueSets"]
        SD["5 StructureDefinitions"]
        Bundle["Validated FHIR R4 Bundle<br/>(Location, Observation, Group, RiskAssessment, Provenance)"]
    end

    subgraph ActionWorkflows [4. Public Health & Clinical Context]
        PublicHealth["Public-Health Advisory & Dossier<br/>(Municipal CommunicationRequest & ECDC Dossier)"]
        Inspection["Field Inspection Request<br/>(Signage & Water Grab Sampling)"]
        CDSHooks["CDS Hooks 1.0 Non-Diagnostic Advisory<br/>(/cds-services/oah-exposure-advisory)"]
        EHR["EHR Exposure Awareness<br/>(Non-Diagnostic Clinical Context)"]
    end

    HeterogeneousInputs --> Ingest
    Ingest --> Score --> Epistemic --> Spatial
    Spatial --> FHIRSuite
    FHIRSuite --> CDSHooks
    CDSHooks --> EHR
    FHIRSuite --> PublicHealth
```

---

## 🎯 Track 7 Standards Conformance Matrix

| Standard / Component | Implementation in OAH-Bridge | Conformance Rationale & File Reference |
| :--- | :--- | :--- |
| **HL7® FHIR® R4** | `4.0.1` Resource Serialization | Complete JSON schema compliance across 8 distinct resources in [`engine/composer.py`](engine/composer.py). |
| **Observation.method** | Strictly Ascertainment Technique | Bound to [`conformance/cs-observation-technique.json`](conformance/cs-observation-technique.json) (`in-situ-sensor-probe`, `citizen-visual-observation`). Epistemic status is NOT conflated. |
| **Epistemic Extension** | `oah-evidence-status` | Standalone extension with `valueCodeableConcept` bound to [`conformance/cs-evidence-status.json`](conformance/cs-evidence-status.json) (`observed`, `inferred`, `confirmed`). |
| **Evidence Metric** | Standalone `Observation` | First-class metric observation linked via `Observation.focus` containing subcomponent telemetry in `Observation.component`. |
| **Definitional Population** | Definitional `Group (actual = false)` | In FHIR R4, `actual = false` designates a definitional exposure cohort; individual membership is not required for the environmental exposure definition. Privacy-preserving cohort representation. |
| **Clinical Disorder Outcome**| `RiskAssessment.prediction.outcome` | Pinned `SNOMED CT International Edition — March 2026 (20260301)` concepts (`40275004`, `416113008`, `69776003`) placed in prediction outcome, distinguishing preferred term from display label. |
| **CDS Hooks 1.0** | Published STU 1.0 Specification | `patient-view` implementation providing informational environmental exposure context; no diagnosis or treatment recommendation. |
| **External Ontologies** | SNOMED CT & HL7 Standard | Integrated with 3/3 active SNOMED CT concepts pinned to `SNOMED CT International Edition — March 2026 (20260301)`, formal Terminology Manifest (`/api/terminology`), and HL7 `risk-probability`. |

---

## 🚀 Quickstart & Reproduction

### 1. Prerequisites
- Python 3.10+
- Modern Web Browser (Chrome, Firefox, Edge, Safari)

### 2. Run the Server
```bash
# Clone the repository
git clone https://github.com/rasmiya06/OneAquaHealth-Bridge.git
cd OneAquaHealth-Bridge

# Start the REST API & CDS Hooks Reference Server
python3 api/server.py 8000
```
Open your browser to: **`http://localhost:8000`**

### 3. Run the Automated Test Suite
```bash
# Run all 25 unit and integration tests
pytest
```
*Result: 25 passed in ~1.03s (100% Pass Rate).*

---

## 🔒 Definitional Cohorts & Privacy Architecture

- **FHIR Group (actual = false)**: Definitional exposure cohort; individual membership is not required for the environmental exposure definition.
- **Privacy-Preserving Cohort Representation**: No patient identifiers, clinical records, or personal locations are ever ingested or transmitted by environmental monitoring systems.
- **Private Network Execution**: Clinical encounter location evaluation occurs entirely **inside the hospital's private EHR network** when a patient encounter triggers the CDS Hook (`patient-view`). Zero personal health data leaves the hospital firewall.
- **Data Minimization by Design**: Aligns with privacy-by-design principles through data minimization, avoiding any tracking of individuals.

---

*Synthetic demonstration data grounded in OneAquaHealth research-city geography. HL7® and FHIR® are registered trademarks of Health Level Seven International.*
