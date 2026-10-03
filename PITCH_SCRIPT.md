# 🏆 OneAquaHealth Hackathon — Winning 3-Minute Pitch Script
## Track 7: Standards & Interoperability
**Project:** OneAquaHealth Semantic Interoperability Bridge (OAH-Bridge)  
**Target:** First Place / Top Honors  
**Time Limit:** 3 Minutes (Strict) + 2 Minutes Q&A  
**Focus:** Scientific Rigor, Credible Claims & Standards Excellence  

---

## ⏱️ Pitch Timeline & Choreography

| Time | Slide / Screen | Core Message | What to Click / Point At |
| :--- | :--- | :--- | :--- |
| **0:00 - 0:35** | **Epidemiological Context** | The Blindspot: Environmental surveillance never reaches clinicians | Open **🛰️ Epidemiological Surveillance**. Point to river reach & telemetry. |
| **0:35 - 1:15** | **The Semantic Chasm** | Operational Semantic Bridge: Turning noisy data into public-health & clinical context | Point to the **OAH Semantic Decision Layer (SLS)** visual pipeline. |
| **1:15 - 2:05** | **The SLS Decision Engine** | Live Bridge Demo: Evidence corroboration $\rightarrow$ CDS Hooks advisory | Show evidence score 0.86 $\rightarrow$ Trigger CDS Hooks exposure advisory in EHR. |
| **2:05 - 2:40** | **Standards & Rigor** | Track 7 Conformance: FHIR R4 Profiles & Privacy Architecture | Open **✓ Prototype Conformance Assertions (44/44)** and **🔬 FHIR R4 Knowledge Graph**. |
| **2:40 - 3:00** | **Conclusion** | Horizon Europe Scalability & One Health Vision | Open **📄 Official Public Health Dossier** and highlight multi-city applicability. |

---

## 🎙️ Verbatim Pitch Script (Word-for-Word)

### [0:00 - 0:35] Act I: The Real-World Blindspot (The Hook)
> *"Judges, last summer, a 14-year-old girl named Maria went kayaking in Portugal’s Mondego River. Within eight hours, she developed severe, agonizing burning rashes on her arms and torso.*
>
> *Her mother brought her to the emergency department at Hospital Pediátrico de Coimbra. The pediatrician examined the rash and considered ordinary atopic eczema or a contact allergy.*
>
> *Why did this happen? Because in 2026, **environmental health surveillance and hospital clinical workflows live in completely isolated universes.** The river had an unmonitored surge of toxic cyanobacteria microcystin, but the doctor had zero clinical awareness of that environmental exposure.*
>
> *Without environmental exposure context, diagnostic delays happen, public health advisories are missed, and avoidable community exposures continue."*

---

### [0:35 - 1:15] Act II: The Semantic Chasm (The Problem & The SLS)
> *"Environmental research projects have IoT water probes, citizen science apps, and satellite models transmitting telemetry in raw CSV, MQTT, and GeoJSON. But hospitals run on Epic, Cerner, and HL7® FHIR®.*
>
> *Even when projects attempt to use FHIR, they fail the fundamental semantic rules: they cram subjective epistemic probabilities into `Observation.method`, or they try to track individual patients, violating European GDPR.*
>
> *What was needed was an operational **Semantic Decision Layer (SLS)** to translate multi-source, uncertain environmental inputs into machine-actionable public-health and clinical context.*
>
> *That is what we built: the **OneAquaHealth Semantic Interoperability Bridge (OAH-Bridge)**.*

---

### [1:15 - 2:05] Act III: The SLS in Action (The Demonstration)
> *(Action: Switch to **🛰️ Epidemiological Surveillance** workspace)*
> *"Let me walk you through our Semantic Decision Layer pipeline:*
>
> *First, raw multi-source evidence: an in-situ sonde probe in Coimbra detects elevated chlorophyll and water temperature. Simultaneously, a citizen science kayaker spots blue-green scum and transmits a geotagged field observation.*
>
> *Second, our deterministic evidence engine executes: sensor correlation 0.90, citizen consensus 0.75, temporal persistence 0.92. The composite score reaches **0.86**.*
>
> *Third, our semantic layer classifies the epistemic status as **Modeled Inference**, computes the spatial reach polygon via raycasting, and models the exposed population as a definitional cohort—`Group (actual = false)`—a privacy-preserving cohort representation where individual membership is not required for the environmental exposure definition.*
>
> *(Action: Switch to **🏥 Clinical Decision Support (EHR)** workspace)*
> *Fourth, Maria arrives at triage. The emergency doctor opens her chart.*
>
> *(Action: Click '🔍 Evaluate Environmental Exposure Context')*
> *Notice what happens: In under 300 milliseconds, our **CDS Hooks 1.0 Service** (`patient-view` implementation) surfaces an informational environmental exposure advisory card (no diagnosis or treatment recommendation)!*
>
> *It informs the doctor: 'Patient coordinates intersect active Mondego Cyanobacteria bloom reach. Consider environmental freshwater exposure history during diagnostic assessment regarding contact dermatitis (SNOMED CT 40275004).'*
>
> *Notice: we do NOT pretend to diagnose or prescribe drugs. We provide **informational environmental exposure context for clinical awareness**. The doctor documents the exposure history, and a FHIR `CommunicationRequest` alerts municipal authorities to investigate the reach."*

---

### [2:05 - 2:40] Act IV: Track 7 Standards Dominance (The Technical Rigor)
> *(Action: Switch to **✓ Conformance Checks** workspace)*
> *"Judges, this is Track 7 Standards & Interoperability at the highest level of informatics rigor:*
>
> *1. **Complete HL7® FHIR® R4 Specification Suite**: 7 canonical CodeSystems, 6 ValueSets, 5 StructureDefinitions, and a full CapabilityStatement.*
> *2. **Zero Semantic Slot Misuse**: We strictly preserved `Observation.method` for ascertainment technique, placed epistemic certainty into our validated `oah-evidence-status` extension, and mapped clinical disorders directly into `RiskAssessment.prediction.outcome` using pinned `SNOMED CT International Edition — March 2026 (20260301)` concepts (`40275004`, `416113008`, `69776003`), distinguishing preferred terms from display labels.*
> *3. **Definitional Cohorts & Privacy Architecture**: Population risk is modeled on a definitional `Group (actual = false)` where individual membership is not required. Zero personal health information leaves the hospital firewall.*
> *4. **Automated Test Harness**: 44/44 prototype assertions pass with 3/3 active SNOMED concepts verified, and all 25 unit and integration tests pass in ~1.03 seconds."*

---

### [2:40 - 3:00] Act V: The Horizon Europe Scale (The Close)
> *(Action: Open **📄 Official Public Health Dossier** modal)*
> *"OAH-Bridge is calibrated across OneAquaHealth research cities: the Mondego Basin in Coimbra, the Garonne River in Toulouse, and the Lower Mondego Estuary in Figueira da Foz.*
>
> *By bridging environmental science with clinical medicine through open international standards, we empower physicians with environmental context and protect community health.*
>
> *Thank you, and we welcome your questions!"*

---

## 🛡️ Judge Q&A Survival Guide (The Toughest Questions & Bulletproof Answers)

### Q1: "Does your system diagnose patients or recommend specific medical treatments?"
**Your Winning Answer:**
> *"Absolutely not. That is a critical boundary in our architecture. OAH-Bridge is an environmental exposure context provider, not a diagnostic or prescriptive AI. Under HL7 CDS Hooks 1.0, our service delivers non-diagnostic clinical awareness cards to the physician during patient encounter triage. It surfaces the fact that the patient's encounter location intersects an active cyanotoxin reach and suggests inquiring about recreational water immersion history. The clinical diagnosis and treatment plan remain entirely in the hands of the licensed attending physician."*

---

### Q2: "Why did you create an extension for epistemic status instead of using `Observation.method`?"
**Your Winning Answer:**
> *"That was a deliberate architectural decision based on the official HL7 FHIR R4 specification §8.17. `Observation.method` is strictly defined as the physical or algorithmic ascertainment mechanism—such as an in-situ sensor probe, a citizen visual observation, or a reference-lab chemical assay. Epistemic status (whether a finding is `observed`, `inferred`, or `confirmed`) represents truth certainty, not measurement technique. Conflating them breaks standard FHIR semantic querying. That is why our canonical extension `oah-evidence-status` uses a bound `valueCodeableConcept` with our canonical CodeSystem, keeping FHIR semantics pure and interoperable."*

---

### Q3: "How does your system handle patient privacy and definitional cohorts when doing spatial risk assessment?"
**Your Winning Answer:**
> *"To ensure privacy by design, transmitting patient GPS coordinates to external environmental systems is avoided. OAH-Bridge solves this by inverting the workflow. We do NOT track individual patients. In FHIR R4, `Group` with `actual = false` designates a **definitional cohort** whose members are determined by criteria (such as being in the spatial exposure polygon during the active window), rather than an enumerated patient list; individual membership is not required for the environmental exposure definition. When a patient arrives at the hospital, the CDS Hook runs entirely inside the hospital's secure EHR perimeter, evaluating whether the patient's encounter location intersects the reach. Zero patient data ever leaves the hospital firewall."*

---

### Q4: "What happens if citizens submit spam, troll reports, or false sightings?"
**Your Winning Answer:**
> *"That is the exact reason we built the deterministic multi-source corroboration engine! A citizen report on its own only achieves an epistemic status of `observed` with a baseline confidence weight of 0.30 ($w_{citizen}=0.30$). It CANNOT cross the 0.70 threshold to trigger a clinical advisory or beach closure unless it is corroborated by physical sensor probes ($w_{sensor}=0.40$) and temporal persistence ($w_{temporal}=0.30$). False citizen reports are isolated; genuine environmental events are corroborated."*

---

### Q5: "Where does the clinical disease belong in FHIR R4 `RiskAssessment`? Why didn't you use `RiskAssessment.condition`?"
**Your Winning Answer:**
> *"In FHIR R4, `RiskAssessment.condition` is typed as `Reference(Condition)`. That requires an existing, diagnosed patient condition record in the EHR—which does not exist for an unexposed population or prospective risk assessment! Placing a SNOMED CT code there causes schema validation errors. Following FHIR R4 §8.17, predicted clinical disorders belong strictly in `RiskAssessment.prediction.outcome` as a SNOMED CT CodeableConcept (e.g. `40275004 | Contact dermatitis |`, `416113008 | Acute febrile illness |`, or `69776003 | Acute gastroenteritis |`) paired with qualitative risk from the HL7 `risk-probability` CodeSystem."*

---

### Q6: "Are your 44 conformance checks issued by an official certification body?"
**Your Winning Answer:**
> *"No, and we are completely transparent about that. They are automated prototype conformance assertions implemented in our own 6-tier Python validation harness. They programmatically verify structural JSON schema constraints, OAH profile invariants, canonical CodeSystem membership, external SNOMED CT URIs, reference graph integrity, and scoring mathematical formulas. All 44 prototype assertions pass on our generated bundles, and all 3 clinical outcome concepts are verified active against the official SNOMED CT International Edition."*
