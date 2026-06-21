# v1.0-rc3 Release Notes

Final release candidate for the Mexico Equity Intelligence Platform.

> *Transforming market activity into governed, AI-ready data products that power financial intelligence.*

This release packages a reproducible Data Engineering and AI MVP that transforms public Mexican equity market observations into governed data products and controlled information services. It is not a trading system, investment recommender, price prediction platform, or forecasting product.

## Included Capabilities

- Reproducible Docker-based pipeline and runtime.
- Raw, Silver, Gold, Quality, and Metadata layers.
- Gold data products for performance, volatility, liquidity, market trends, and AI-ready insights.
- FastAPI endpoints and a Streamlit executive dashboard.
- Deterministic governed question answering over Gold datasets.
- Optional LLM-assisted answers grounded in structured Gold evidence.
- Guardrails against unsupported topics, forecasts, price targets, and investment recommendations.
- Architecture, operations, data product, monetization, and reviewer documentation.
- Executive presentation in PDF format.

## Changes Since v1.0-rc2

- Added the executive project presentation to the repository.
- Strengthened the README opening with a concise executive value proposition.
- Refined the Project Vision narrative to reduce repetition and improve business positioning.
- Improved dashboard hierarchy with thematic dividers and prominent governed-agent panels.
- Aligned the public review guidance with `v1.0-rc3` as the final release candidate.

## Validation

Final validation completed successfully on June 20, 2026:

```text
Data quality: 15 checks passed, 0 failed
Automated tests: 23 passed
API health: status ok
Dashboard: loads successfully
Latest trading date: 2026-06-19
```

## Review Flow

```bash
git checkout v1.0-rc3
docker compose run --rm pipeline
docker compose run --rm tests
docker compose up
```

Open:

```text
http://localhost:8501
http://localhost:8000/docs
```

The platform works without an OpenAI API key. Real API keys must remain private and must not be committed or included in release materials.
