# BMV Market Intelligence Platform

Local data engineering MVP for Mexican market intelligence data products.

The platform transforms public Mexican market data into governed, reusable, AI-ready data products:

```text
Public Market Data -> Raw -> Silver -> Quality -> Gold -> Metadata -> API -> Governed AI Agent
```

```mermaid
flowchart LR
    Source[Public Market Data] --> Ingestion[Ingestion]
    Ingestion --> Raw[Raw Parquet]
    Raw --> Silver[Silver Transformation]
    Silver --> Quality[Data Quality Gate]
    Quality --> Gold[Gold Data Products]
    Gold --> Metadata[Metadata Catalog]
    Gold --> API[FastAPI]
    Gold --> Dashboard[Streamlit Dashboard]
    Gold --> Agent[Governed AI Agent]
    API --> Users[Business Users]
    Dashboard --> Users
    Agent --> Users
```

## Business Value

This project is not only a price-data pipeline. It demonstrates how market data can be packaged as a business-ready intelligence product.

The platform is framed from the point of view of a stock exchange or financial data provider: raw trades and prices are inputs, but the business sells trusted information, distribution, analytics, access, and decision support.

The platform helps a market data business, exchange, issuer relations team, or financial intelligence provider:

- Convert raw public market prices into reusable data products.
- Offer performance, volatility, liquidity, trend, and AI-ready insight datasets.
- Expose governed datasets through APIs for downstream customers and applications.
- Give analysts and business users a dashboard for fast market monitoring.
- Use a Governed AI Agent that answers only from controlled Gold datasets, reducing hallucination risk.
- Create a foundation for premium subscriptions, executive reports, alerts, and sector intelligence products.

## Stock Exchange Business Context

A stock exchange monetizes more than transactions. It can create business value by packaging market activity into products for issuers, brokers, investors, fintechs, data vendors, research teams, and internal commercial teams.

This MVP shows how that information business can work:

- **Issuers** can understand how their stock compares with sector behavior, liquidity, and market attention.
- **Brokers and analysts** can consume ranked performance, risk, liquidity, and trend signals.
- **Fintechs and data vendors** can integrate curated market intelligence through APIs.
- **Internal exchange teams** can use dashboards and reports to support issuer relations, market development, and premium data services.
- **Executives** can receive explainable summaries instead of raw price tables.

## Monetization Strategy

The Gold layer is designed as the commercial product layer. Each dataset answers a business question that can become a paid feature:

- **API subscriptions:** endpoints for performance, volatility, liquidity, trends, and insights.
- **Premium dashboard:** analyst-facing market intelligence views for monitoring issuers and sectors.
- **Market alerts:** unusual volume, elevated volatility, underperformance, or sustained growth signals.
- **Executive reports:** recurring summaries generated from governed Gold datasets.
- **AI assistant:** a controlled question-answering interface over trusted market intelligence products.

The commercial idea is simple: the value is not the raw price history; the value is the governed layer that turns data into decisions, APIs, alerts, and explainable AI responses.

## Prerequisites

- [Git](https://git-scm.com/downloads/) to clone the repository
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) with Docker Compose
- Internet access for Yahoo Finance downloads
- Available local ports: `8000` for the API and `8501` for the dashboard

No local Python installation, cloud account, API token, paid BMV service, or BMV credentials are required.

## Quick Start

Clone the repository and enter the project folder:

```bash
git clone https://github.com/Yhodiux/bmv-market-intelligence-platform.git
cd bmv-market-intelligence-platform
```

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

- [Business Pitch](docs/business_pitch.md)
- [Executive Summary](docs/executive_summary.md)
- [Data Flow Architecture](docs/architecture/data_flow.md) including transformation highlights
- [Cloud Roadmap](docs/architecture/cloud_roadmap.md)
- [Data Contracts](docs/architecture/data_contracts.md)
- [Operational Readiness](docs/architecture/operational_readiness.md)
- [Data Products](docs/architecture/data_products.md)
- [Business KPIs and OKRs](docs/business_kpis_okrs.md)
- [Demo Guide](docs/demo_guide.md)

## Review Map

| Capability | Where to Review |
| --- | --- |
| Reproducible pipeline | `docker-compose.yml`, `src/ingestion/`, `src/transformation/`, `src/gold/` |
| Data quality gates | `src/quality/validate_data_quality.py`, `data/metadata/data_quality_report.json` |
| Governed data products | `data/gold/`, `docs/architecture/data_products.md` |
| Metadata catalog | `src/metadata/build_metadata.py`, `data/metadata/datasets_metadata.json` |
| API distribution | `src/api/main.py`, `http://localhost:8000/docs` |
| Dashboard consumption | `src/dashboard/app.py`, `docs/screenshots/` |
| Governed AI guardrails | `src/ai_agent/market_agent.py`, `tests/test_market_agent.py` |
| Operational thinking | `docs/architecture/operational_readiness.md` |
| Cloud evolution | `docs/architecture/cloud_roadmap.md` |
| Business monetization | `docs/business_pitch.md`, `docs/architecture/data_products.md` |
| KPIs and OKRs | `docs/business_kpis_okrs.md` |

## Data Engineering Perspective

This repository is structured so reviewers can inspect the engineering decisions directly:

- **Reproducible execution:** Docker Compose runs the pipeline, API, dashboard, and tests without local Python setup.
- **Layered data architecture:** Raw, Silver, Gold, Metadata, and Quality stages are separated by responsibility.
- **Quality as a gate:** validation runs before Gold product publication and writes an auditable report.
- **Data products:** Gold datasets are shaped around business questions, not generic tables.
- **Consumption interfaces:** the same governed datasets feed API endpoints, dashboard views, the deterministic Governed AI Agent, and the optional LLM-governed assistant.
- **Governance and operations:** data contracts, operational readiness, KPIs/OKRs, and cloud migration are documented.
- **Production evolution:** Airflow/MWAA, dbt, cloud storage, API management, usage metering, and larger-scale RAG over documents are roadmap options, not current dependencies.

## Demo Preview

### Dashboard Overview

![Dashboard overview](docs/screenshots/dashboard_overview.png)

### Dashboard Analytics

![Dashboard analytics](docs/screenshots/dashboard_analytics.png)

### Deterministic Governed AI Agent

![Deterministic Governed AI Agent](docs/screenshots/deterministic_agent.png)

### LLM-Governed Market Assistant

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
- `GET /questions`
- `POST /ask`
- `POST /ask-llm`

## Run Dashboard

After running the pipeline, start the local Streamlit dashboard:

```bash
docker compose up dashboard
```

Open:

```text
http://localhost:8501
```

## Ask the Governed AI Agent

The platform exposes two governed AI modes:

- `/ask` is deterministic and answers supported business questions with fully auditable logic.
- `/ask-llm` is an optional LLM-governed assistant that builds structured context from Gold datasets and uses the model only to write a natural-language answer.

Both modes reject out-of-domain questions, forecasts, price targets, and buy/sell recommendations instead of inventing unsupported answers.

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"Which issuers had the best 30-day performance?\"}"
```

Use `GET /questions` to list the current governed question set.

Example LLM-governed request:

```bash
curl -X POST http://localhost:8000/ask-llm \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"Explain WALMEX.MX in executive terms.\"}"
```

The LLM-governed assistant is optional. To enable model-backed answers, set:

```text
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4.1-mini
ENABLE_LLM_AGENT=true
```

If `OPENAI_API_KEY` is not configured, `/ask-llm` still returns the Gold evidence packet and a controlled configuration message.

Supported questions include:

- Which issuers had the best 30-day performance?
- Which issuers show sustained growth with controlled volatility?
- Which sectors show higher volatility?
- Which companies show unusual volume behavior?
- What are the most relevant market insights?
- Which issuers had the weakest 30-day performance?
- Which issuers have the highest liquidity?
- Which issuers have high risk levels?
- Which sectors had the strongest 30-day performance?
- Show me the latest market snapshot.
- Summarize WALMEX.MX.
- Compare WALMEX.MX and CEMEXCPO.MX.

## Run Tests

Run the automated test suite with Docker:

```bash
docker compose run --rm tests
```
