# Agentic Agricultural Data Platform

A modular starter implementation of the uploaded workflow: profiling → schema mapping → Bronze → ETL → validation/repair → Silver → EDA/features → Gold → crop analytics.

## Features
- CSV, JSON and Excel upload
- Data profiling: schema, missingness, duplicates, cardinality and memory
- Agricultural semantic schema mapping with confidence and review flags
- Bronze raw-file preservation
- Conservative, auditable ETL repairs
- Validation score and quality checks
- Silver and Gold CSV layers
- Feature engineering for weather interactions and numeric normalization
- Interactive Streamlit dashboard and basic safe text-to-analytics intents
- Crop classifier baseline when labelled crop data is available
- Docker deployment starter

## Run locally
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501.

## Run with Docker
```bash
docker build -t agri-agent .
docker run -p 8501:8501 agri-agent
```

## Data expectations
Useful columns include nitrogen, phosphorus, potassium, ph, temperature, humidity, rainfall, crop and yield. Column names are suggestions, not mandatory.

## Important ML limitations
The crop recommendation model is a baseline, not agronomic advice. A supervised model requires representative labelled examples and evaluation on a held-out test set. Historical crop frequency is explicitly labelled as a fallback and must not be interpreted as suitability. Yield prediction is not yet trained because it requires a defined yield target and sufficient labelled data.

## Production hardening checklist
- Replace local folders with object storage and PostgreSQL metadata.
- Add authentication, authorization, upload limits and malware scanning.
- Add dataset versioning, lineage and immutable Bronze storage.
- Execute generated code only in an isolated, resource-limited sandbox. This starter deliberately does not execute arbitrary LLM-generated code.
- Add human approval for schema changes and high-impact repairs.
- Add tests, model evaluation, drift monitoring and audit retention.
- Configure an LLM provider and approved tool schemas before enabling autonomous natural-language actions.

## Architecture
`app.py` → `agri_platform.pipeline` → independent agents under `agri_platform/agents/`.

The pipeline is deterministic by default so it can be tested and audited. LangGraph/LLM orchestration can be added as a separate layer after the core data contracts and evaluation tests are stable.

## External API integrations (Gemini, Groq, Open-Meteo, SoilGrids)

1. Copy `.env.example` to `.env`.
2. Add keys from https://aistudio.google.com/apikey and https://console.groq.com/keys.
3. Install with `pip install -r requirements.txt`, then run `streamlit run app.py`.

Gemini is attempted first. If its request fails (quota, timeout, key/model error), Groq is attempted. If both are unavailable, the deterministic pipeline still runs and schema mapping falls back to local rules. Never commit `.env` to Git.

Open-Meteo geocoding and forecast endpoints require no API key. Use the **Live Agriculture Intelligence APIs** section to fetch current weather and a forecast. SoilGrids is queried for pH, clay, sand and soil organic carbon at 0–5 cm. Its REST v2 endpoint is beta and may be temporarily paused; the app reports an unavailable response rather than making up values. Check ISRIC status/docs before relying on it in production.

The AI integration generates text and schema-mapping suggestions only. It does not execute arbitrary LLM-generated Python or SQL. Review schema suggestions before production use.


## Included dataset

The project includes `data/Indian_crop_production_yield_dataset.csv` (575,879 rows). In the Streamlit sidebar, choose **Included Indian crop dataset** and click **Run agentic pipeline**. Columns: State_Name, District_Name, Crop_Year, Season, Crop, Area, Production and yield. This is historical crop-production data; it does not contain rainfall, temperature or measured soil variables. Weather and SoilGrids integrations remain separate enrichment services and require location/coordinate input.
