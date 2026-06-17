# BMV Market Intelligence Platform

Local data engineering MVP for Mexican market intelligence data products.

The platform transforms public Mexican market data into governed, reusable, AI-ready data products:

```text
Public Market Data -> Raw -> Silver -> Quality -> Gold -> Metadata -> API -> AI Agent
```

## Quick Start

Run the full local pipeline:

```bash
docker compose run --rm pipeline
```

Run tests:

```bash
docker compose run --rm tests
```

Start the dashboard:

```bash
docker compose up dashboard
```

Open:

```text
http://localhost:8501
```

Start the API:

```bash
docker compose up api
```

Open:

```text
http://localhost:8000/docs
```

## Architecture

- [Executive Summary](docs/executive_summary.md)
- [Data Flow Architecture](docs/architecture/data_flow.md)
- [Data Products](docs/architecture/data_products.md)
- [Demo Guide](docs/demo_guide.md)

## Demo Preview

### Dashboard Overview

![Dashboard overview](docs/screenshots/dashboard_overview.png)

### Dashboard Analytics

![Dashboard analytics](docs/screenshots/dashboard_analytics.png)

### AI Agent

![Dashboard AI Agent](docs/screenshots/dashboard_ai_agent.png)

### API Market Question

![Ask best performance](docs/screenshots/ask_best_performance.png)

### API Guardrails

![Ask guardrail](docs/screenshots/ask_guardrail.png)

## Run pipeline

This pipeline downloads daily historical prices from Yahoo Finance, writes raw Parquet files under `data/raw/`, builds the standardized Silver dataset under `data/silver/`, writes a data quality report under `data/metadata/`, and generates Gold data products under `data/gold/`.

```bash
docker compose run --rm pipeline
```

The pipeline uses the ticker universe defined in `config/tickers.json`.

## Gold datasets

The Gold layer currently generates:

- `gold_performance.parquet`
- `gold_volatility.parquet`
- `gold_liquidity.parquet`
- `gold_market_trends.parquet`
- `gold_ai_insights.parquet`

## Run API

After running the pipeline, start the local API:

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

## Run Dashboard

After running the pipeline, start the local Streamlit dashboard:

```bash
docker compose up dashboard
```

Open:

```text
http://localhost:8501
```

## Ask the Agent

The `/ask` endpoint answers supported market intelligence questions using the Gold datasets.

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"Which issuers had the best 30-day performance?\"}"
```

Supported questions include:

- Which issuers had the best 30-day performance?
- Which issuers show sustained growth with controlled volatility?
- Which sectors show higher volatility?
- Which companies show unusual volume behavior?
- What are the most relevant market insights?

## Run Tests

Run the automated test suite with Docker:

```bash
docker compose run --rm tests
```
