# Business KPIs and OKRs

## Purpose

This document connects the market intelligence platform to measurable business outcomes.

The MVP already produces technical and data-product metrics such as row counts, quality status, Gold dataset counts, API responses, and Governed AI Agent guardrail behavior. In production, those metrics can become business KPIs for adoption, monetization, reliability, and customer value.

## KPI Framework

| KPI Area | KPI | Why It Matters | Current MVP Evidence | Production Target Example |
| --- | --- | --- | --- | --- |
| Data quality | Quality checks passed | Customers only trust products built from valid data | `15/15` checks passed in `data_quality_report.json` | Greater than 99% successful quality runs |
| Data freshness | Latest available trading date | Market intelligence loses value when stale | Latest dates available in Gold datasets | Gold datasets published before market open or agreed SLA |
| Product coverage | Number of issuers and sectors covered | Coverage defines commercial usefulness | Ticker universe in `config/tickers.json` | Expand to full licensed coverage by product tier |
| Data product breadth | Number of Gold products available | More product surfaces create more monetization paths | 5 Gold datasets | Add alerts, issuer benchmarking, and sector packs |
| API readiness | Endpoints available over governed datasets | APIs are the distribution channel for data subscriptions | FastAPI endpoints for Gold products | Authenticated API usage by customer and endpoint |
| Dashboard value | Executive views available | Non-technical users need fast interpretation | Streamlit dashboard with KPIs, charts, and insights | Active users, session frequency, and saved views |
| AI trust | Unsupported questions rejected safely | Prevents invented claims and protects trust | Guardrail test for unsupported questions | Unsupported-answer rate monitored and reviewed |
| Commercial usage | Product consumption by customer | Shows which datasets create value | Not metered in local MVP | Usage metering for billing and product prioritization |
| Revenue enablement | Sellable product tiers defined | Turns platform capability into packaging | Basic, Professional, Enterprise tiers documented | Paid subscriptions, renewals, and expansion revenue |

## Suggested OKRs

### Objective 1: Turn Market Data Into Trusted Data Products

Key results:

- Publish Raw, Silver, Gold, and Metadata outputs through one reproducible pipeline.
- Keep critical data quality checks passing before publishing Gold products.
- Maintain documented data contracts for each layer and consumer-facing endpoint.
- Provide reviewer-ready evidence through metadata, quality reports, screenshots, and tests.

### Objective 2: Increase Decision Value for Financial Users

Key results:

- Provide business-ready products for performance, volatility, liquidity, market trends, and AI-ready insights.
- Support questions that combine performance, risk, liquidity, and sector context.
- Expose the same governed datasets through dashboard, API, and Governed AI Agent interfaces.
- Document demo questions that explain the business value to non-technical users.

### Objective 3: Prepare the Platform for Monetization

Key results:

- Define product lines for API subscriptions, dashboards, alerts, reports, and AI assistant access.
- Map Gold datasets to buyer groups such as issuers, brokers, analysts, fintechs, data vendors, and internal exchange teams.
- Define subscription tiers and enterprise capabilities such as entitlements, usage metering, and SLAs.
- Keep the architecture ready for licensed data sources and cloud deployment.

### Objective 4: Protect Trust in AI-Assisted Market Intelligence

Key results:

- Ground Governed AI Agent answers only in Gold datasets.
- Return source datasets and supporting data points with answers.
- Reject unsupported external or predictive questions instead of inventing responses.
- Maintain automated tests for supported and unsupported Governed AI Agent behavior.

## Current MVP Scorecard

| Area | Current Status |
| --- | --- |
| Pipeline reproducibility | Implemented with Docker Compose |
| Data quality | Implemented with blocking validation and JSON report |
| Gold data products | 5 datasets generated |
| Metadata catalog | Implemented |
| API distribution | Implemented with FastAPI |
| Dashboard consumption | Implemented with Streamlit |
| AI guardrails | Implemented with deterministic supported-question handling |
| Automated tests | Implemented |
| Business monetization framing | Documented |
| Production usage metering | Roadmap item |
| Authentication and customer entitlements | Roadmap item |
| Paid subscription tracking | Roadmap item |

## Business Interpretation

The platform should not be measured only by whether data pipelines run. A market intelligence product should also be measured by whether it produces trusted, fresh, explainable, and reusable information that customers can consume through APIs, dashboards, reports, alerts, or controlled AI interfaces.

For this MVP, the KPIs and OKRs show the intended path from technical execution to business value:

```text
Quality data -> Governed products -> Customer consumption -> Usage measurement -> Monetization
```
