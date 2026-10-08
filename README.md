# ORACLE-X

### Autonomous Enterprise Decision Engine

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)

> **ORACLE-X** is a portfolio project focused on deterministic, evidence-driven decision engineering for business operations.



ORACLE-X is a deterministic, evidence-driven enterprise decision engine designed to transform business signals into validated operational decisions.

It combines historical business data, simulated business scenarios, anomaly detection, root-cause analysis, multi-agent reasoning, decision validation, outcome tracking, and optional LLM-based evidence interpretation.

> **Design principle:** deterministic business logic owns the facts and decisions. The LLM is used only for interpretation and executive communication.

## Contents

- [What ORACLE-X Does](#what-oracle-x-does)
- [Core Capabilities](#core-capabilities)
- [Provenance Model](#provenance-model)
- [Validation Example](#validation-example)
- [Historical Business Dataset](#historical-business-dataset)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Local Setup](#local-setup)
- [API](#api)
- [Dashboard](#dashboard)
- [Testing](#testing)
- [Data & Repository Policy](#data--repository-policy)
- [Design Principles](#design-principles)
- [Current Limitations](#current-limitations)
- [Roadmap](#roadmap)
- [Project Status](#project-status)
- [Author](#author)


---

## What ORACLE-X Does

ORACLE-X follows a complete decision pipeline:

```text
Business Data
     ↓
Business World / Current State
     ↓
Scenario Simulation
     ↓
Anomaly Detection
     ↓
Investigation
     ↓
Evidence Synthesis
     ↓
Root-Cause Analysis
     ↓
Multi-Agent Debate
     ↓
Decision Generation
     ↓
Decision Validation
     ↓
Decision Memory
     ↓
Outcome Tracking
     ↓
Learning Signals
     ↓
Adaptive Intelligence
     ↓
Optional LLM Interpretation
```

The system is designed to separate:

- observed historical facts
- deterministic model-derived metrics
- simulated scenario changes
- deterministic root-cause analysis
- observed decision outcomes
- LLM-generated interpretation

This separation provides traceability and reduces the risk of allowing an LLM to invent business facts.

---

## Core Capabilities

### 1. Business Intelligence

ORACLE-X builds a structured business view from historical data, including:

- order activity
- revenue
- customers
- products
- sellers
- reviews
- inventory
- seller risk
- operational activity

### 2. Scenario Simulation

The simulation layer creates controlled business scenarios to test the decision engine.

The current scenario library contains 18 scenarios, including:

- Baseline Stable
- Mild Demand Growth
- Moderate Demand Increase
- Inventory Pressure
- Low Cover Only
- Demand-Supply Imbalance
- Strong Demand Shock
- Severe Supply Shock
- Extreme Demand Shock
- Detection Boundary
- Recovery
- Inventory Recovery
- Customer Experience Decline
- Full Business Stress
- Critical Inventory
- Supplier and Customer Risk
- Demand-Only Surge
- Inventory-Only Critical

Simulation data is explicitly treated as simulated rather than historical.

### 3. Deterministic Anomaly Detection

The current detection engine includes the:

`DEMAND_SUPPLY_IMBALANCE`

rule.

The rule requires all of the following:

- demand increase >= 15%
- inventory cover decline >= 20%
- current inventory cover <= 10 days

The detector also maintains rule versioning and prevents duplicate detection for the same snapshot/rule/version combination.

### 4. Investigation Engine

The InvestigationEngine coordinates the full investigation workflow.

It combines:

- Finance Agent
- Operations Agent
- Risk Agent
- Customer Agent
- Evidence Synthesizer
- Root Cause Analyzer
- Debate Engine
- Decision Engine
- Decision Validator
- Learning Engine
- Decision Quality Evaluator
- Adaptive Intelligence

### 5. Root-Cause Analysis

The deterministic RCA layer evaluates candidate causes including:

1. Demand Surge
2. Inventory Pressure
3. Supplier Pressure
4. Customer Experience Deterioration

The system distinguishes evidence from interpretation and avoids unsupported causal certainty.

### 6. Decision Validation

Every generated decision passes through deterministic validation before it can enter the decision-memory and learning pipeline.

A validated decision can then be:

- persisted
- evaluated
- tracked
- used to generate learning signals

### 7. Decision Memory & Learning

ORACLE-X stores validated decisions and their outcomes.

The learning layer evaluates decision quality and extracts learning signals from observed outcomes.

Adaptive intelligence remains read-only when learning data is insufficient rather than fabricating confidence.

### 8. LLM Interpretation

The LLM is deliberately constrained.

It does **not** own:

- business metrics
- anomaly detection
- root-cause facts
- decision validation
- simulation state
- historical calculations

Instead, it interprets already-produced evidence and generates executive-level explanations.

Current implementation uses the Groq Python client and reads the API key from environment configuration.

---

## Provenance Model

ORACLE-X preserves the origin of important information.

| Data / Result                | Provenance                        |
| ---------------------------- | --------------------------------- |
| Historical business data     | `OBSERVED_HISTORICAL`             |
| Inventory level and coverage | `MODEL_DERIVED`                   |
| Scenario changes             | `SIMULATED`                       |
| Root-cause interpretation    | `DETERMINISTIC_RCA`               |
| Learning signals             | `DETERMINISTIC_OBSERVED_OUTCOMES` |
| Adaptive intelligence        | `DETERMINISTIC_READ_ONLY`         |
| LLM interpretation           | `LLM_EVIDENCE_INTERPRETATION`     |

This provenance model is a core trust mechanism of the system.

---

## Validation Example

The production system currently contains 7 retained incidents.

The investigation API has been tested end-to-end against Incident `2`.

The validated investigation produced:

- investigation ID: `INV-2-7`
- decision status: `ACTIONABLE`
- decision validation: `VALID`
- decision memory ID: `4`
- learning status: `LEARNING_SIGNALS_EXTRACTED`
- decision quality: `STRUCTURALLY_STRONG`
- decision quality score: `1.0`

Adaptive intelligence correctly reported insufficient learning data rather than producing an unsupported adaptive conclusion.

---

## Historical Business Dataset

The project uses the Brazilian E-Commerce Public Dataset by Olist as the historical business foundation.

The analyzed historical period contains:

- 99,441 orders
- 112,650 order items
- 3,095 sellers
- 99,224 reviews
- 23 seller states

For the investigated August 2018 business window:

- 5,954 total orders
- 5,855 delivered orders
- 5,997 active customers
- $798,785.87 item revenue
- $134.16 canonical AOV
- 4.25 average review score
- 4,079 inventory products
- 14.00 days inventory cover

Raw source data is intentionally excluded from Git tracking.

---

## Architecture

```
```

```
                    ┌─────────────────────┐
                    │   Historical Data   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Business Intelligence│
                    └──────────┬──────────┘
                               │
                 ┌─────────────┴─────────────┐
                 ▼                           ▼
        ┌─────────────────┐        ┌─────────────────┐
        │ Scenario Engine │        │ Current State   │
        └────────┬────────┘        └────────┬────────┘
                 │                           │
                 └─────────────┬─────────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Detection Engine    │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Investigation Engine│
                    └──────────┬──────────┘
                               ▼
              ┌─────────────────────────────────┐
              │ Agents + Evidence + RCA + Debate│
              └────────────────┬────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Decision Engine     │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Decision Validator  │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Memory / Learning   │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ LLM Interpretation  │
                    └─────────────────────┘
```

---

## Project Structure

```
```

```
ORACLE-X/
│
├── api/
│   └── main.py
│
├── config/
│   └── settings.py
│
├── data/
│   └── oracle_x.db              # local / ignored
│
├── legacy/
│   ├── build_database.py
│   ├── build_world.py
│   └── investigate_incident.py
│
├── src/
│   ├── agents/
│   ├── data/
│   ├── debate/
│   ├── decision/
│   ├── intelligence/
│   ├── investigation/
│   ├── learning/
│   ├── simulation/
│   └── validation/
│
├── tests/
│   ├── test_adaptive_intelligence.py
│   └── test_llm_interpreter.py
│
├── app.py
├── inspect_schema.py
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Tech Stack

- Python
- FastAPI
- Streamlit
- SQLite
- Pandas
- NumPy
- Requests
- Groq Python SDK
- python-dotenv

---

## Local Setup

### 1. Clone the repository

```
```

```
git clone <YOUR_REPOSITORY_URL>
cd ORACLE-X
```

### 2. Create a virtual environment

Windows PowerShell:

```
```

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```
```

```
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and provide the required API key.

Example:

```
```

```
GROQ_API_KEY=your_groq_api_key_here
```

Never commit `.env`.

### 5. Run the API

```
```

```
uvicorn api.main:app --reload
```

The API runs locally on:

```
```

```
http://127.0.0.1:8000
```

### 6. Run the dashboard

In a second terminal:

```
```

```
streamlit run app.py
```

The Streamlit dashboard connects to the local FastAPI service at:

```
```

```
http://127.0.0.1:8000
```

---

## API

The local API exposes the core investigation workflow through FastAPI.

### Health Check

```
```

```
GET /health
```

Example:

```
```

```
Invoke-RestMethod http://127.0.0.1:8000/health
```

Expected response:

```
```

```
{
  "status": "ok",
  "service": "ORACLE-X API"
}
```

### Investigate an Incident

```
```

```
POST /investigate/{incident_id}
```

Example:

```
```

```
Invoke-RestMethod -Method Post `
  http://127.0.0.1:8000/investigate/2
```

### Investigation Summary

```
```

```
POST /investigate/{incident_id}/summary
```

### Read Investigation Summary

```
```

```
GET /investigate/{incident_id}/summary
```

Example:

```
```

```
Invoke-RestMethod `
  http://127.0.0.1:8000/investigate/2/summary
```

---

## Dashboard

The Streamlit dashboard provides an enterprise-style interface for reviewing:

- business health
- investigation results
- decisions
- validation
- root causes
- provenance
- learning signals
- LLM interpretation

The dashboard currently expects the FastAPI service to be running locally on port `8000`.

---

## Testing

The repository includes tests for key intelligence components:

```
```

```
pytest
```

For API validation, start FastAPI and verify:

```
```

```
Invoke-RestMethod http://127.0.0.1:8000/health
```

Then execute an investigation:

```
```

```
Invoke-RestMethod -Method Post `
  http://127.0.0.1:8000/investigate/2
```

---

## Data & Repository Policy

Raw Olist CSV files are intentionally excluded from Git tracking because they are large and are not required to understand the source code.

The production SQLite database is also excluded from Git tracking.

This keeps the public repository focused on:

- architecture
- decision logic
- investigation logic
- simulation
- learning
- validation
- API
- dashboard
- tests

Local data can be restored separately when required.

---

## Design Principles

### Deterministic First

Business facts and decision authority are implemented through deterministic Python and SQL logic.

### Evidence Before Interpretation

The system produces structured evidence before asking an LLM to explain it.

### Provenance Everywhere

Important outputs identify whether they are historical, derived, simulated, deterministic, or LLM-generated.

### No Unsupported Causality

The RCA layer distinguishes candidate explanations from proven causal relationships.

### Fail Safely

When evidence is insufficient, ORACLE-X prefers an explicit insufficient-evidence state instead of manufacturing confidence.

### LLM as Interpreter

The LLM improves explanation and executive communication without becoming the source of business truth.

---

## Current Limitations

ORACLE-X is currently a local portfolio implementation.

The current Streamlit dashboard expects the FastAPI service to be available locally at `127.0.0.1:8000`.

Adaptive intelligence also requires sufficient observed decision outcomes before it can provide stronger learned signals.

The system should therefore be viewed as a decision-engineering prototype rather than a fully autonomous production enterprise platform.

---

## Roadmap

Potential next steps include:

- production deployment architecture
- hosted API and dashboard
- stronger authentication and authorization
- richer automated monitoring
- broader outcome datasets
- expanded decision-quality evaluation
- stronger adaptive learning with sufficient outcomes
- CI/CD
- production observability
- automated data refresh pipelines

---

## Project Status

ORACLE-X currently includes:

- deterministic business intelligence
- 18 simulation scenarios
- anomaly detection
- investigation orchestration
- multi-agent analysis
- evidence synthesis
- deterministic root-cause analysis
- decision generation
- decision validation
- decision memory
- outcome tracking
- learning signals
- adaptive intelligence
- optional LLM evidence interpretation
- FastAPI API
- Streamlit dashboard
- automated tests

The core investigation workflow has been validated end-to-end.

---

## Author

**Eng.Abdelrahman Akl**

ORACLE-X is a portfolio project focused on:

- AI decision systems
- enterprise intelligence
- deterministic AI architecture
- business analytics
- decision validation
- explainable AI
- agentic workflows

---

## License

Add the preferred project license before publishing the repository.\
