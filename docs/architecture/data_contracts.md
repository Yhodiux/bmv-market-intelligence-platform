# Data Contracts

## Purpose

Data contracts define the expected structure, quality rules, ownership, and consumers for each dataset layer.

The MVP already validates core Raw and Silver quality rules in code. This document makes those expectations explicit so the platform can evolve toward production governance, customer-facing APIs, and monetized data products.

## Contract Principles

- Raw preserves source-aligned market observations.
- Silver provides cleaned, typed, enriched analytical records.
- Gold provides business-ready data products shaped around use cases.
- Metadata describes available datasets and supports discoverability.
- API and AI Agent consumers should rely on Gold datasets, not Raw files.
- Critical quality checks must block publication of downstream products.

## Dataset Ownership

| Layer | Logical Owner | Responsibility |
| --- | --- | --- |
| Raw | Ingestion pipeline | Source extraction, schema preservation, raw file availability |
| Silver | Transformation pipeline | Standardization, typing, enrichment, derived fields |
| Data Quality | Quality validation layer | Contract validation and failure blocking |
| Gold | Data product pipeline | Business metrics, rankings, signals, AI-ready products |
| Metadata | Governance layer | Dataset catalog, descriptions, counts, columns, paths |
| API | Product serving layer | Expose Gold products to applications and users |
| Dashboard / AI Agent | Consumption layer | Use governed Gold products for visualization and answers |

## Raw Contract

Dataset:

```text
data/raw/market_prices_raw.parquet
```

Expected columns:

| Column | Type Expectation | Required | Description |
| --- | --- | --- | --- |
| `date` | date-compatible | Yes | Market trading date |
| `ticker` | string | Yes | Issuer ticker symbol |
| `open` | numeric | Yes | Opening price |
| `high` | numeric | Yes | Daily high price |
| `low` | numeric | Yes | Daily low price |
| `close` | numeric | Yes | Closing price |
| `adj_close` | numeric | Yes | Adjusted closing price |
| `volume` | numeric | Yes | Trading volume |

Quality expectations:

- Dataset must exist.
- Row count must be greater than zero.
- Required columns must be present.
- Prices and volume should be non-negative after transformation.

Primary consumers:

- Silver transformation.
- Data quality validation.

## Silver Contract

Dataset:

```text
data/silver/market_prices_silver.parquet
```

Expected columns:

| Column | Type Expectation | Required | Description |
| --- | --- | --- | --- |
| `date` | date | Yes | Market trading date |
| `ticker` | string | Yes | Issuer ticker symbol |
| `open_price` | numeric | Yes | Standardized opening price |
| `high_price` | numeric | Yes | Standardized high price |
| `low_price` | numeric | Yes | Standardized low price |
| `close_price` | numeric | Yes | Standardized close price |
| `adjusted_close` | numeric | Yes | Standardized adjusted close |
| `volume` | numeric | Yes | Trading volume |
| `daily_return` | numeric | Yes | `(close_price - open_price) / open_price` |
| `intraday_volatility` | numeric | Yes | `(high_price - low_price) / open_price` |
| `price_range` | numeric | Yes | `high_price - low_price` |
| `volume_category` | string | Yes | Issuer-relative activity band |
| `trend_flag` | string | Yes | `Bullish`, `Bearish`, or `Neutral` |
| `issuer_name` | string | Yes | Business issuer name |
| `sector` | string | Yes | Issuer sector |
| `ingestion_timestamp` | timestamp/string | Yes | Pipeline generation timestamp |

Quality expectations:

- Dataset must exist.
- Row count must be greater than zero.
- Required columns must be present.
- `ticker` must not be null.
- `date` must not be null.
- `(ticker, date)` must be unique.
- Prices must be non-negative.
- Volume must be non-negative.
- `high_price` must be greater than or equal to `low_price`.
- `close_price` must be between `low_price` and `high_price` when values are comparable.
- Issuer metadata must exist for every ticker.

Primary consumers:

- Data quality validation.
- Gold data product generation.
- Metadata catalog.

## Gold Contracts

Gold datasets are product contracts. They are shaped for business consumption, APIs, dashboards, and AI Agent answers.

### gold_performance

Dataset:

```text
data/gold/gold_performance.parquet
```

Expected columns:

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

Business contract:

- Provides issuer performance over 7, 30, and 90 days.
- Supports ranking by 30-day return.
- Supports performance categories such as outperformer, underperformer, and neutral.

Consumers:

- API `/performance`.
- AI Agent supported performance questions.
- Dashboard performance rankings.

### gold_volatility

Dataset:

```text
data/gold/gold_volatility.parquet
```

Expected columns:

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

Business contract:

- Provides rolling volatility windows.
- Classifies issuer risk levels.
- Supports sector and issuer risk analysis.

Consumers:

- API `/volatility`.
- AI Agent supported volatility questions.
- Dashboard risk and volatility views.

### gold_liquidity

Dataset:

```text
data/gold/gold_liquidity.parquet
```

Expected columns:

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

Business contract:

- Provides liquidity and volume activity metrics.
- Detects unusual volume behavior against recent issuer activity.
- Supports liquidity rankings and alert products.

Consumers:

- API `/liquidity`.
- AI Agent supported volume questions.
- Dashboard liquidity and unusual volume sections.

### gold_market_trends

Dataset:

```text
data/gold/gold_market_trends.parquet
```

Expected columns:

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

Business contract:

- Compares issuer movement against sector behavior.
- Measures issuer participation within its sector.
- Supports market trend and divergence analysis.

Consumers:

- API `/market-trends`.
- Dashboard trend views.
- Future sector intelligence products.

### gold_ai_insights

Dataset:

```text
data/gold/gold_ai_insights.parquet
```

Expected columns:

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

Business contract:

- Converts market signals into concise business interpretations.
- Provides AI-ready insight summaries grounded in computed Gold metrics.
- Supports follow-up analyst questions.

Consumers:

- API `/ai-insights`.
- AI Agent relevant insight questions.
- Dashboard AI insights section.
- Future executive reports or alert products.

## Metadata Contract

Dataset:

```text
data/metadata/datasets_metadata.json
```

Expected fields per dataset:

```text
dataset_name
layer
record_count
column_count
columns
created_at
source
business_description
path
```

Business contract:

- Every published dataset should appear in the metadata catalog.
- Metadata should describe both technical structure and business use.
- Consumers should be able to discover available data products without reading code.

## API Contract

The API serves Gold datasets and metadata.

Endpoints:

```text
GET /health
GET /datasets
GET /performance
GET /volatility
GET /liquidity
GET /market-trends
GET /ai-insights
POST /ask
```

API expectations:

- Endpoints should return structured JSON.
- Data product endpoints should be sourced from Gold datasets.
- `/ask` should answer only supported market intelligence questions.
- Unsupported questions should return supported alternatives instead of invented answers.

## Contract Enforcement

Implemented in the MVP:

- Required Raw and Silver column checks.
- Row-count checks.
- Non-null checks for Silver ticker and date.
- Uniqueness checks for Silver ticker-date records.
- Non-negative checks for prices and volume.
- Price consistency checks.
- Pipeline failure when critical data quality checks fail.
- Automated tests for Gold outputs, metadata, API behavior, and AI Agent behavior.

Recommended production extensions:

- Formal schema validation with Great Expectations, Pandera, or Glue Data Quality.
- Versioned contracts for each Gold data product.
- Backward compatibility rules for API consumers.
- Dataset freshness SLAs.
- Schema-change alerts.
- Data owner and steward assignment.
- Customer-facing product SLAs for paid datasets.

## Change Management

Any future schema change should answer:

- Which dataset contract changes?
- Is the change backward compatible?
- Which API endpoint or dashboard view is affected?
- Which AI Agent question depends on the changed field?
- Does the metadata catalog need to be updated?
- Do tests and quality checks need to be updated?

For monetized data products, contract changes should be treated like product changes, not only code changes.
