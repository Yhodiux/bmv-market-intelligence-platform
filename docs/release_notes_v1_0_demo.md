# v1.0-demo Release Notes

Stable review version for the Mexico Equity Intelligence Platform.

Positioning:

```text
Transforming public market data into AI-ready data products for Market Intelligence and data monetization.
```

This release is not a trading system, investment recommender, price prediction platform, or forecasting product. It demonstrates governed data engineering, data products, APIs, dashboards, and AI-enabled natural-language access over curated Market Intelligence datasets.

## What This Release Demonstrates

This release packages a local, reproducible market intelligence MVP that turns public Mexican market data into governed data products, API endpoints, dashboard views, and controlled AI-assisted analysis.

The project is framed as a data product platform for a stock exchange, market data provider, issuer relations team, broker, analyst group, or financial intelligence business.

## Main Capabilities

- Docker-based local execution for pipeline, API, dashboard, and tests.
- Raw, Silver, Gold, Quality, and Metadata data layers.
- Gold data products for performance, volatility, liquidity, market trends, and AI-ready insights.
- FastAPI endpoints for governed access to Gold datasets.
- Streamlit dashboard for market monitoring and business review.
- Deterministic Governed AI Agent for auditable business questions.
- Optional LLM-governed assistant using OpenAI over structured Gold evidence.
- Guardrails that block out-of-domain questions, forecasts, price targets, and buy/sell recommendations.
- Documentation for architecture, data products, operations, cloud roadmap, business value, and demo review.

## Roadmap Position

- Phase 1, current MVP: Raw/Silver/Gold architecture, AI agent, APIs, dashboard, and Market Intelligence data products.
- Phase 2: RAG and LLM enrichment over governed content.
- Phase 3: Forecasting models such as Prophet, ARIMA, or LSTM as future Advanced Analytics extensions.
- Phase 4: Anomaly detection for market and operational signals.
- Phase 5: Personalized recommendations for dashboards, alerts, reports, and API products without investment advice.

## Review Entry Points

- README: `README.md`
- Demo guide: `docs/demo_guide.md`
- Dashboard: `http://localhost:8501`
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

## Suggested Review Flow

```bash
git checkout v1.0-demo
docker compose run --rm pipeline
docker compose run --rm tests
docker compose up
```

Recommended API checks:

- `GET /questions`
- `POST /ask` with `Which issuers had the best 30-day performance?`
- `POST /ask-llm` with `Explain WALMEX.MX in executive terms.`
- Guardrail check: `Who won the World Cup?`
- Guardrail check: `Should I buy WALMEX.MX today?`

## OpenAI API Key

The project runs without an OpenAI API key. In that mode, the deterministic agent works normally and `/ask-llm` returns governed evidence with a controlled configuration message.

To enable real model-backed LLM answers, create `.env` from `.env.example` and set `OPENAI_API_KEY`. OpenAI API usage can generate costs and requires billing or credits.

No real API key is committed to this repository.

## Expected Test Result

```text
23 passed
```

## Version

Tag:

```text
v1.0-demo
```
