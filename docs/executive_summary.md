# Executive Summary

## Project Overview

The BMV Market Intelligence Platform is a local, Docker-based data engineering and AI MVP for Mexican market intelligence.

It transforms public historical market data into governed, reusable, AI-ready data products:

```text
Public Market Data -> Raw -> Silver -> Quality -> Gold -> Metadata -> API -> Dashboard -> Governed AI Agent
```

The project is designed to be reproducible by an evaluator without BMV credentials, paid services, cloud accounts, or local Python setup.

## Business Problem

Public market data is useful, but raw prices alone are not a monetizable product. The platform demonstrates how public issuer data can be transformed into curated data products that support:

- Market performance monitoring
- Risk and volatility intelligence
- Liquidity and trading activity analysis
- Sector and issuer trend discovery
- AI-ready insights grounded in governed datasets

From a stock exchange or financial data provider perspective, this is the core business idea: market activity becomes more valuable when it is governed, packaged, distributed, and explained for specific customers. The MVP therefore demonstrates not only technical data engineering, but also how information can become a commercial product.

Potential customers include issuers, brokers, analysts, fintechs, data vendors, executive teams, and issuer relations teams.

## Technical Scope

The MVP implements:

- Docker Compose orchestration
- Yahoo Finance ingestion through `yfinance`
- Raw, Silver, and Gold data layers
- Data quality validation
- Metadata catalog generation
- FastAPI data product API
- Governed AI Agent
- Streamlit dashboard
- Automated tests
- Architecture and demo documentation

## Data Product Layers

### Raw

Raw market prices are stored as Parquet files and preserve the source structure:

```text
date
ticker
open
high
low
close
adj_close
volume
```

### Silver

Silver standardizes and enriches Raw data with issuer metadata and derived metrics:

```text
daily_return
intraday_volatility
price_range
volume_category
trend_flag
issuer_name
sector
ingestion_timestamp
```

### Gold

Gold turns market data into reusable data products:

- `gold_performance`
- `gold_volatility`
- `gold_liquidity`
- `gold_market_trends`
- `gold_ai_insights`

These datasets support dashboards, APIs, and grounded AI answers.

## Governed AI Strategy

The Governed AI Agent is deterministic and domain-constrained.

It answers supported market intelligence questions using Gold datasets as the source of truth. Unsupported questions return suggested supported questions instead of invented answers.

This design demonstrates AI guardrails:

- No external claims
- No unsupported predictions
- Source datasets included in responses
- Structured data points returned with answers

## Dashboard Demo

### Dashboard Overview

The dashboard starts with dataset status, KPIs, executive overview, and 30-day performance rankings.

![Dashboard overview](screenshots/dashboard_overview.png)

### Analytics Sections

The analytics view includes risk, volatility, liquidity, unusual volume, and supporting tables.

![Dashboard analytics](screenshots/dashboard_analytics.png)

### Governed AI Agent in Dashboard

The dashboard includes AI-ready insights and an embedded Market Intelligence Agent question selector.

![Dashboard AI Agent](screenshots/dashboard_ai_agent.png)

## API Demo

### Supported Ask Request

The `/ask` endpoint returns structured answers grounded in Gold Performance data.

![Ask best performance](screenshots/ask_best_performance.png)

### Guardrail Behavior

Unsupported questions are rejected safely with suggested supported market intelligence questions.

![Ask guardrail](screenshots/ask_guardrail.png)

## How to Run

Run the full pipeline:

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

Start the API:

```bash
docker compose up api
```

## Evaluation Highlights

- Fully local and reproducible with Docker
- No paid BMV services or credentials required
- Data quality checks built into the pipeline
- Gold datasets framed as monetizable data products
- Business framing aligned with exchange-style market data products
- API and dashboard consume the same governed datasets
- Governed AI Agent is grounded, auditable, and domain-constrained
- Automated tests validate core behavior

## Recommended Review Path

1. Run the pipeline.
2. Run tests.
3. Open the dashboard.
4. Review performance, volatility, liquidity, and insights.
5. Ask a supported market intelligence question.
6. Ask an unsupported question to verify guardrails.
7. Review FastAPI `/docs`.
