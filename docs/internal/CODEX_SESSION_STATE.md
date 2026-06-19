# Codex Session State

## Current Status

The project currently implements the local Raw, Silver, Gold, Metadata, Data Quality, API, Dashboard, AI Agent, documentation, and demo preview layers for the BMV Market Intelligence Platform MVP.

Current saved status date:

```text
2026-06-18 America/Mexico_City
```

Expected Git status after saving and pushing this snapshot:

```text
main synchronized with origin/main
```

## Implemented

- Docker Compose pipeline service.
- Yahoo Finance ingestion script.
- Ticker configuration with Mexican market issuers.
- Raw Parquet output under `data/raw/`.
- Silver transformation script.
- Silver Parquet output under `data/silver/`.
- Data quality validation script.
- Data quality JSON report under `data/metadata/`.
- Gold data product build script.
- Gold Parquet outputs under `data/gold/`.
- Dataset metadata catalog under `data/metadata/`.
- FastAPI service exposing Gold data products.
- Deterministic AI Agent endpoint grounded in Gold datasets.
- Optional LLM-governed assistant endpoint grounded in Gold evidence.
- Automated pytest suite for Gold outputs, metadata, API, and AI Agent behavior.
- Architecture documentation for data flow and Gold data products.
- Data flow documentation includes Silver and Gold transformation highlights.
- Data flow documentation includes a Mermaid architecture diagram rendered by GitHub.
- Mermaid data flow now shows API, Dashboard, and AI Agent delivering value to business consumers and monetized data products.
- Data flow documentation includes a BMV source assessment explaining why public BMV pages and Web Services were not used for the reproducible historical MVP.
- AWS cloud roadmap documenting how to migrate the local MVP into managed cloud storage, orchestration, API serving, monitoring, security, and monetization enablement.
- Data contracts documentation covering Raw, Silver, Gold, Metadata, API contracts, enforcement, ownership, and change management.
- Operational readiness documentation covering failure handling, blocking quality checks, operational metrics, monitoring, production roadmap, monetized API, AI assistant grounding, and customer entitlements.
- Demo guide for reviewers.
- Executive summary with dashboard/API screenshots.
- README demo preview section with dashboard and API screenshots.
- README business value and monetization strategy sections.
- README prerequisites section for external local execution.
- README prerequisites include official Git and Docker Desktop installation links.
- README Quick Start includes `git clone` and `cd bmv-market-intelligence-platform` before Docker commands.
- Business pitch document for remote evaluation and business-facing delivery.
- Streamlit dashboard with Gold dataset preview, executive KPIs, performance charts, risk/volatility charts, liquidity/volume views, AI insights, and an embedded AI Agent question selector.
- Internal project notes moved under `docs/internal/` so the repository root stays clean for reviewers.
- Project status snapshot updated for the current release candidate.

## Important Adjustments Made

- Updated `yfinance` from `0.2.50` to `1.4.1` because the older version failed with `JSONDecodeError` against Yahoo Finance.
- Replaced `AMXL.MX` with `AMXB.MX` because `AMXL.MX` returned no Yahoo Finance data, while `AMXB.MX` worked.
- Updated ingestion normalization to handle the `MultiIndex` columns returned by newer `yfinance` versions.

## Key Files

- `README.md`
- `docker-compose.yml`
- `requirements.txt`
- `config/tickers.json`
- `src/ingestion/ingest_yfinance.py`
- `src/transformation/build_silver.py`
- `src/quality/validate_data_quality.py`
- `src/gold/build_gold.py`
- `src/metadata/build_metadata.py`
- `src/api/main.py`
- `src/ai_agent/market_agent.py`
- `tests/test_gold_build.py`
- `tests/test_metadata.py`
- `tests/test_market_agent.py`
- `tests/test_api.py`
- `tests/test_llm_agent.py`
- `docs/architecture/data_flow.md`
- `docs/architecture/data_products.md`
- `docs/architecture/cloud_roadmap.md`
- `docs/architecture/data_contracts.md`
- `docs/architecture/operational_readiness.md`
- `docs/business_pitch.md`
- `docs/demo_guide.md`
- `docs/executive_summary.md`
- `docs/internal/CODEX_SESSION_STATE.md`
- `docs/internal/PROJECT_CONTEXT_FOR_CODEX.md`
- `docs/screenshots/`
- `docs/screenshots/dashboard_overview.png`
- `docs/screenshots/dashboard_analytics.png`
- `docs/screenshots/dashboard_ai_agent.png`
- `docs/screenshots/ask_best_performance.png`
- `docs/screenshots/ask_guardrail.png`
- `src/dashboard/app.py`
- `data/raw/market_prices_raw.parquet`
- `data/silver/market_prices_silver.parquet`
- `data/metadata/data_quality_report.json`
- `data/metadata/datasets_metadata.json`
- `data/gold/gold_performance.parquet`
- `data/gold/gold_volatility.parquet`
- `data/gold/gold_liquidity.parquet`
- `data/gold/gold_market_trends.parquet`
- `data/gold/gold_ai_insights.parquet`

## Reproduce Current Pipeline

```bash
docker compose run --rm pipeline
```

The pipeline now executes:

1. `python src/ingestion/ingest_yfinance.py`
2. `python src/transformation/build_silver.py`
3. `python src/quality/validate_data_quality.py`
4. `python src/gold/build_gold.py`
5. `python src/metadata/build_metadata.py`

## Last Successful Validation

The latest successful full pipeline run was executed with:

```bash
docker compose run --rm pipeline
```

It generated:

- Raw dataset: `data/raw/market_prices_raw.parquet`
- Silver dataset: `data/silver/market_prices_silver.parquet`
- Data quality report: `data/metadata/data_quality_report.json`
- Row count: `12,570` rows in both Raw and Silver
- Silver columns: `16`
- No null values in the expected Silver columns
- Data quality status: `passed`
- Data quality checks: `15` passed, `0` failed
- Gold performance rows: `12,570`
- Gold volatility rows: `12,570`
- Gold liquidity rows: `12,570`
- Gold market trends rows: `12,570`
- Gold AI insights rows: `10`

Latest test validation was executed with:

```bash
docker compose run --rm tests
```

Result:

```text
23 passed
```

Silver derived fields include:

- `daily_return`
- `intraday_volatility`
- `price_range`
- `volume_category`
- `trend_flag`
- `issuer_name`
- `sector`
- `ingestion_timestamp`

## Notes

Git may report `dubious ownership` in this environment. For Git inspection commands, use:

```bash
git -c safe.directory=F:/Proyectos/bmv-market-intelligence-platform status --short
```

The repository should be clean and synchronized with `origin/main` after saving and pushing this snapshot.

## Runtime Services

Start the local API and dashboard together with:

```bash
docker compose up
```

Open:

```text
http://localhost:8501
http://localhost:8000/docs
```

Available endpoints:

- `GET /health`
- `GET /datasets`
- `GET /performance`
- `GET /volatility`
- `GET /liquidity`
- `GET /market-trends`
- `GET /ai-insights`
- `GET /questions`
- `POST /ask`
- `POST /ask-llm`

## Tests

Run:

```bash
docker compose run --rm tests
```

## Final Delivery Status

The project is ready to be sent by repository link and is ready for external tester validation.

Recommended tester validation:

```text
git clone https://github.com/Yhodiux/bmv-market-intelligence-platform.git
cd bmv-market-intelligence-platform
docker compose run --rm pipeline
docker compose run --rm tests
docker compose up
```

Expected tester outcome:

- Pipeline completes without errors.
- Tests return `23 passed`.
- Dashboard opens at `http://localhost:8501`.
- API docs open at `http://localhost:8000/docs`.

Recommended delivery message:

```text
Hola, comparto el repositorio del proyecto:

https://github.com/Yhodiux/bmv-market-intelligence-platform

El proyecto implementa un MVP local de Data Engineering + AI para inteligencia de mercado mexicana/BMV. Incluye pipeline Raw/Silver/Gold, validaciones de calidad, catalogo de metadata, API FastAPI, dashboard Streamlit, AI Agent con respuestas fundamentadas en datasets Gold, documentacion y screenshots de demo.

Se puede ejecutar localmente con Docker:

docker compose run --rm pipeline
docker compose run --rm tests
docker compose up

La suite de pruebas queda validada con 23 tests passing.
```

## Current Release Notes

- Recommended review tag: `v1.0-rc1`
- Previous stable demo tag: `v1.0-demo`
- Current public branch: `main`
- Current state: clean, synchronized with GitHub, and ready for release/tag review.
