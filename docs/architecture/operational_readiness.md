# Operational Readiness

## Purpose

Operational readiness explains how the platform should be monitored, supported, and evolved from a local MVP into a production data product platform.

The goal is to show that the solution is not only buildable, but also operable: failures should be visible, quality gates should block bad data, and product consumers should have reliable datasets, APIs, dashboards, and AI answers.

## Current MVP Operation

The current MVP runs locally through Docker Compose.

Core commands:

```bash
docker compose run --rm pipeline
docker compose run --rm tests
docker compose up
```

Pipeline execution:

```text
Ingestion -> Silver Transformation -> Data Quality -> Gold Build -> Metadata Build
```

The MVP already includes:

- Reproducible Docker execution.
- Explicit pipeline stages.
- Data quality validation.
- Pipeline failure when critical quality checks fail.
- Generated metadata catalog.
- Automated tests for data products, metadata, API, and Governed AI Agent behavior.
- Local API and dashboard services.

## Failure Handling

### If Ingestion Fails

Possible causes:

- Internet connectivity issue.
- Yahoo Finance response issue.
- Ticker unavailable or renamed.
- Source schema change.
- Empty response from the provider.

Expected behavior:

- The ingestion script should fail clearly instead of producing empty downstream products.
- Raw files should not be treated as valid if no rows are generated.
- The pipeline should stop before Silver, Gold, API, or AI outputs are refreshed with invalid data.

Operational response:

- Check connectivity.
- Identify failed ticker.
- Review source response.
- Confirm whether the ticker changed or was delisted.
- Re-run the pipeline after correcting configuration or source availability.

### If Transformation Fails

Possible causes:

- Missing Raw dataset.
- Missing expected Raw columns.
- Invalid numeric values.
- Missing issuer metadata.

Expected behavior:

- Silver generation should fail with a clear error.
- Missing metadata should block enrichment.
- Downstream Gold products should not be regenerated from incomplete Silver data.

Operational response:

- Review Raw schema.
- Review `config/tickers.json`.
- Confirm issuer metadata fields.
- Re-run the Silver and downstream stages after correction.

### If Data Quality Fails

The data quality layer is a blocking gate.

Critical checks that block the pipeline:

- Raw row count is zero.
- Silver row count is zero.
- Required Raw columns are missing.
- Required Silver columns are missing.
- Silver `ticker` is null.
- Silver `date` is null.
- Duplicate `(ticker, date)` records exist.
- Prices are negative.
- Volume is negative.
- `high_price` is lower than `low_price`.
- `close_price` falls outside the comparable low/high range.

Expected behavior:

- The data quality report is written to `data/metadata/data_quality_report.json`.
- If critical checks fail, the pipeline raises an error.
- Gold products should not be published from failed Silver data.

Operational response:

- Inspect failed check names in the quality report.
- Review sample invalid rows when available.
- Correct source, transformation, or metadata issues.
- Re-run the pipeline.

### If API or Dashboard Fails

Possible causes:

- Gold datasets missing.
- Pipeline not run before serving.
- Port conflict on `8000` or `8501`.
- Dependency installation issue inside container.

Expected behavior:

- API and dashboard should fail visibly rather than silently returning invented data.
- The README and demo guide instruct users to run the pipeline before starting services.

Operational response:

- Run `docker compose run --rm pipeline`.
- Confirm Gold files exist under `data/gold/`.
- Confirm ports `8000` and `8501` are available.
- Restart the relevant Docker Compose service.

## Operational Metrics

The platform should monitor both data health and service health.

### Data Pipeline Metrics

- Pipeline start and end time.
- Pipeline duration.
- Number of tickers processed.
- Raw row count.
- Silver row count.
- Gold row count by dataset.
- Data quality status.
- Number of passed and failed quality checks.
- Dataset freshness timestamp.
- Schema changes by dataset.
- Missing or failed tickers.

### Data Product Metrics

- Number of Gold datasets published.
- Latest available trading date.
- Number of records per Gold product.
- Number of AI-ready insights generated.
- Distribution of risk levels.
- Count of unusual volume signals.
- Count of outperformers and underperformers.

### API Metrics

- Request count by endpoint.
- Error rate by endpoint.
- Latency by endpoint.
- `/ask` supported vs unsupported question count.
- Most used data product endpoints.
- Empty response count.

### Dashboard Metrics

- Dashboard availability.
- Page load time.
- Dataset load failures.
- User interaction with Governed AI Agent question selector.

## Monitoring Design for Production

In AWS, operational monitoring could use:

- CloudWatch Logs for job, API, and dashboard logs.
- CloudWatch Metrics for duration, failures, latency, and error rates.
- CloudWatch Alarms for failed jobs, stale data, API errors, and quality failures.
- SNS or Slack integration for failure notifications.
- S3 event logs or object metadata for dataset publication tracking.
- API Gateway metrics for request volume, throttling, and usage.

Recommended alerts:

- Pipeline failed.
- Ingestion produced zero rows.
- Data quality status is `failed`.
- Gold dataset was not updated by expected time.
- API error rate exceeds threshold.
- API latency exceeds threshold.
- Dashboard cannot load Gold datasets.
- Unsupported Governed AI Agent question volume increases unexpectedly.

## MVP to Production Roadmap

### Stage 1: MVP Local

Current state:

- Docker Compose local execution.
- Public Yahoo Finance data.
- Raw, Silver, Gold, Metadata layers.
- Data quality checks.
- FastAPI service.
- Streamlit dashboard.
- Governed AI Agent.
- Tests and documentation.

Purpose:

- Prove the product concept.
- Demonstrate data engineering and AI grounding.
- Provide a reproducible technical assessment artifact.

### Stage 2: Production Data Platform

Target capabilities:

- Scheduled pipeline orchestration.
- Cloud object storage for Raw, Silver, and Gold zones.
- Dataset catalog and governance.
- Quality checks with alerts.
- Incremental ingestion.
- Partitioned datasets.
- CI/CD for jobs and services.
- Centralized logging and monitoring.

Purpose:

- Make the data product reliable, observable, and maintainable.

### Stage 3: Monetized API

Target capabilities:

- API authentication.
- API keys or OAuth.
- Customer-specific access control.
- Rate limits and quotas.
- Usage metering by customer and endpoint.
- Product tiers by dataset or endpoint.
- API documentation for external consumers.

Purpose:

- Turn Gold datasets into paid data product endpoints.

### Stage 4: Governed AI Assistant with RAG/LLM Grounding

Target capabilities:

- LLM integration through a managed provider such as Amazon Bedrock.
- Retrieval over Gold datasets and metadata.
- Prompt templates tied to supported business questions.
- Source dataset references in answers.
- Guardrails against unsupported claims.
- Evaluation tests for answer quality and factual grounding.

Purpose:

- Improve natural-language access while keeping Gold datasets as the source of truth.

### Stage 5: Customer Entitlements and Subscriptions

Target capabilities:

- Customer and tenant model.
- Subscription tiers.
- Dataset-level entitlements.
- Endpoint-level entitlements.
- Usage tracking for billing.
- Customer-specific dashboards or API scopes.
- Audit logs for access and consumption.

Purpose:

- Move from internal platform to commercial market intelligence product.

## Production Runbook Outline

For a production deployment, the team should maintain a runbook with:

- Pipeline schedule and expected completion time.
- Data freshness SLA.
- Quality check descriptions and failure actions.
- Source availability troubleshooting.
- Ticker configuration update process.
- API restart process.
- Dashboard restart process.
- Incident severity levels.
- Escalation contacts.
- Customer communication process for product outages.

## Readiness Summary

The MVP is intentionally local, but it already has the operational foundation needed for production:

- Clear pipeline stages.
- Explicit data quality gate.
- Reusable Gold data products.
- Metadata catalog.
- API and dashboard consumers.
- Governed AI Agent with bounded behavior.
- Tests that validate key contracts.

The next operational step is to add managed orchestration, monitoring, alerts, access control, and usage metering so the platform can support a production and monetized data product model.
