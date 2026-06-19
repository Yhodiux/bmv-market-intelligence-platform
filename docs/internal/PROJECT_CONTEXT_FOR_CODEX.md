# Project Context for Codex

## Project Name

Mexico Equity Intelligence & Data Products Platform

---

## Objective

Build a local, Docker-based Data Engineering + Artificial Intelligence project for a technical assessment related to Bolsa Mexicana de Valores (BMV).

The project must demonstrate:

- Data Engineering
- Data ingestion
- Raw / Silver / Gold data layers
- Data quality
- Metadata management
- Data products
- API layer
- AI Agent
- Monetization strategy

This is not only a financial analysis project. It must look like a real data product platform that transforms public market data into monetizable information products.

---

## Key Product Vision

The objective is to demonstrate how public stock market data can be transformed into governed, reusable, AI-ready and monetizable data products.

The value is not only the extraction of market data.

The value is the full pipeline:

```text
Data -> Quality -> Products -> API -> AI -> Monetization
```

---

## Important Scope Decision

The MVP must run locally and must not depend on:

- Paid BMV services
- BMV credentials
- Tokens
- Authorized IPs
- Commercial licenses
- Evaluator-owned cloud accounts

The MVP will not use BMV Web Services.

BMV Web Services were reviewed during the assessment research, but they are not used because they require commercial access and controlled connectivity. The objective of this MVP is to provide a fully reproducible solution that any evaluator can execute locally with Docker.

---

## Data Source Strategy

### Business Domain

Bolsa Mexicana de Valores / Mexican stock market.

### Technical MVP Data Source

Yahoo Finance through the `yfinance` Python library.

### Reason

Yahoo Finance provides public historical daily market data suitable for the MVP:

- Open
- High
- Low
- Close
- Adjusted Close
- Volume
- Historical daily data
- No credentials required
- Docker-friendly execution
- Reproducible by any evaluator

### Important Clarification

Yahoo Finance is used only as the technical data source for the MVP.

The business framing remains focused on the Mexican stock market and equity intelligence data products.

---

## Current Architecture

```text
Public Market Data
        ↓
Ingestion Layer
        ↓
Raw Zone
        ↓
Data Quality
        ↓
Silver Zone
        ↓
Gold Zone
        ↓
Metadata Layer
        ↓
API Services
        ↓
AI Agent
        ↓
Data Products
```

---

## Local Technology Stack

Use a simple local stack:

- Python
- Pandas
- yfinance
- DuckDB
- Parquet
- FastAPI
- Streamlit
- Docker
- Docker Compose
- Optional later: OpenAI-compatible LLM API

Avoid complex cloud dependencies for now.

---

## Initial Market Universe

Use representative Mexican issuers related to the IPC universe.

Initial tickers:

```text
AMXL.MX
WALMEX.MX
GFNORTEO.MX
GMEXICOB.MX
CEMEXCPO.MX
BIMBOA.MX
FEMSAUBD.MX
KOFUBL.MX
TLEVISACPO.MX
KIMBERA.MX
```

Historical window:

```text
5 years
```

Frequency:

```text
Daily
```

---

## Expected Raw Layer

Raw data should preserve source structure as much as possible.

Expected fields:

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

Raw output location:

```text
data/raw/
```

Preferred format:

```text
parquet
```

CSV is acceptable only if needed for debugging.

---

## Silver Layer

Silver must clean, standardize, type, and enrich the raw data.

Expected Silver fields:

```text
date
ticker
open_price
high_price
low_price
close_price
adjusted_close
volume
daily_return
intraday_volatility
price_range
volume_category
trend_flag
issuer_name
sector
ingestion_timestamp
```

Derived metrics:

```text
daily_return = (close_price - open_price) / open_price

intraday_volatility = (high_price - low_price) / open_price

price_range = high_price - low_price
```

Trend flag logic:

```text
Bullish if daily_return > 0
Bearish if daily_return < 0
Neutral if daily_return == 0
```

Volume category:

Use relative ranking or quantiles:

```text
Low
Medium
High
```

Silver output location:

```text
data/silver/
```

---

## Gold Layer

Gold should represent monetizable data products, not only analytical tables.

Create these datasets:

---

### 1. gold_performance

Purpose:

Identify winners, losers, and sustained performance.

Metrics:

```text
ticker
issuer_name
sector
date
return_7d
return_30d
return_90d
performance_rank_30d
performance_category
```

---

### 2. gold_volatility

Purpose:

Measure risk and volatility.

Metrics:

```text
ticker
issuer_name
sector
date
volatility_7d
volatility_30d
volatility_90d
risk_level
```

---

### 3. gold_liquidity

Purpose:

Measure trading activity and market participation.

Metrics:

```text
ticker
issuer_name
sector
date
volume
avg_volume_30d
max_volume_30d
min_volume_30d
volume_variation_pct
liquidity_score
liquidity_rank
```

---

### 4. gold_market_trends

Purpose:

Identify trends by issuer and sector.

Metrics:

```text
ticker
issuer_name
sector
date
trend_flag
sector_avg_return_30d
issuer_return_30d
market_participation
trend_strength
```

---

### 5. gold_ai_insights

Purpose:

Generate AI-ready business insights.

Fields:

```text
ticker
issuer_name
sector
date
insight_title
insight_summary
business_interpretation
recommended_question
severity
```

---

## Data Quality

Implement basic quality checks:

- No null ticker
- No null date
- No duplicate ticker-date records
- Prices must be greater than or equal to zero
- Volume must be greater than or equal to zero
- high_price >= low_price
- close_price must be between low_price and high_price when possible
- Raw input row count must be greater than zero
- Silver output row count must be greater than zero

Output data quality report to:

```text
data/metadata/data_quality_report.json
```

---

## Metadata

Create metadata output with:

```text
dataset_name
layer
record_count
column_count
columns
created_at
source
business_description
```

Output location:

```text
data/metadata/
```

---

## API Layer

Create FastAPI service with endpoints:

```text
GET /health
GET /datasets
GET /performance
GET /volatility
GET /liquidity
GET /market-trends
GET /ai-insights
```

Later:

```text
POST /ask
```

---

## AI Agent

The AI Agent should answer natural language questions using the Gold datasets.

Example questions:

```text
Which issuers had the best 30-day performance?
Which issuers show sustained growth with controlled volatility?
Which sectors show higher volatility?
Which companies show unusual volume behavior?
What are the most relevant market insights?
```

Important:

The AI Agent must not invent numbers. It should answer based on the Gold datasets.

---

## Project Folder Structure

Expected structure:

```text
mexico-equity-intelligence-platform/
├── README.md
├── docker-compose.yml
├── .env.example
├── requirements.txt
├── Makefile
│
├── docs/
│   ├── architecture/
│   │   ├── data_flow.md
│   │   └── data_sources.md
│   ├── screenshots/
│   └── deck/
│
├── data/
│   ├── raw/
│   ├── silver/
│   ├── gold/
│   └── metadata/
│
├── src/
│   ├── ingestion/
│   ├── transformation/
│   ├── quality/
│   ├── gold/
│   ├── metadata/
│   ├── api/
│   ├── ai_agent/
│   └── reporting/
│
├── scripts/
├── tests/
└── notebooks/
```

---

## First Implementation Tasks

Start with the local pipeline, not the AI Agent.

Recommended order:

1. Create requirements.txt
2. Create ticker configuration file
3. Create ingestion script using yfinance
4. Save Raw parquet files
5. Create Silver transformation
6. Create Data Quality validation
7. Create Gold datasets
8. Create metadata generator
9. Create FastAPI endpoints
10. Create simple AI Agent

---

## Coding Guidelines

Use clear, simple Python.

Prefer:

- pandas
- yfinance
- duckdb
- pathlib
- logging
- pydantic where useful

Avoid overengineering.

Every script should be executable locally.

Every output path should be relative to the project root.

Use functions.

Add logs.

Fail clearly when data is missing.

---

## Recommended First Prompt for Codex

Read `docs/internal/PROJECT_CONTEXT_FOR_CODEX.md` and help me implement the first local MVP step by step.

Start only with:

1. `requirements.txt`
2. ticker configuration file
3. ingestion script using yfinance
4. Raw parquet output under `data/raw/`

Do not build the full project at once.
