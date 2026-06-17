# Codex Session State

## Current Status

The project currently implements the local Raw, Silver, Gold, Metadata, Data Quality, API, Dashboard, AI Agent, documentation, and demo preview layers for the BMV Market Intelligence Platform MVP.

The latest delivery-content commit is:

```text
6bec892 Add supported API question screenshot to README
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
- Automated pytest suite for Gold outputs, metadata, API, and AI Agent behavior.
- Architecture documentation for data flow and Gold data products.
- Demo guide for reviewers.
- Executive summary with dashboard/API screenshots.
- README demo preview section with dashboard and API screenshots.
- Streamlit dashboard with Gold dataset preview, executive KPIs, performance charts, risk/volatility charts, liquidity/volume views, AI insights, and an embedded AI Agent question selector.

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
- `docs/architecture/data_flow.md`
- `docs/architecture/data_products.md`
- `docs/demo_guide.md`
- `docs/executive_summary.md`
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

Post-pipeline tests were executed with:

```bash
docker compose run --rm tests
```

Result:

```text
9 passed
```

The latest post-outage validation was also confirmed by the user:

```text
9 passed
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

The repository was clean and synchronized with `origin/main` after the latest delivery-content push to:

```text
6bec892 Add supported API question screenshot to README
```

## API

Start the local API with:

```bash
docker compose up api
```

Available endpoints:

- `GET /health`
- `GET /datasets`
- `GET /performance`
- `GET /volatility`
- `GET /liquidity`
- `GET /market-trends`
- `GET /ai-insights`
- `POST /ask`

## Dashboard

Start the local dashboard with:

```bash
docker compose up dashboard
```

Then open:

```text
http://localhost:8501
```

## Tests

Run:

```bash
docker compose run --rm tests
```

## Recommended Next Step

Optional next steps:

- Review the GitHub README rendering with screenshots.
- Start the dashboard and API for a final live demo check.
- Add a formal PPTX or PDF presentation only if the delivery requires that format.
