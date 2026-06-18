# Cloud Roadmap

## Purpose

The current MVP runs locally with Docker so any evaluator can reproduce it without cloud accounts, paid services, credentials, or special infrastructure.

The same design can be moved to AWS because the project already separates ingestion, transformation, quality, Gold data products, metadata, API, dashboard, and Governed AI Agent logic. The local Docker setup is the portable execution layer; AWS would provide managed storage, orchestration, serving, monitoring, security, and scale.

This roadmap describes production evolution options. Airflow, dbt, managed cloud services, LLMs, and RAG are not current MVP dependencies.

The current product position is Market Intelligence and data monetization, not market prediction. Forecasting models are a possible later Advanced Analytics phase, after governance, data quality, product APIs, access control, and commercial packaging are established.

## Current Local Architecture

```text
Docker Compose
  -> Ingestion
  -> Raw Parquet
  -> Silver Transformation
  -> Data Quality
  -> Gold Data Products
  -> Metadata Catalog
  -> FastAPI
  -> Streamlit Dashboard
  -> Governed AI Agent
```

This is intentionally simple for the MVP, but it already follows the same logical layers expected in a production data platform.

## AWS Target Architecture

```text
Market Data Sources
  -> Ingestion Job
  -> Amazon S3 Raw Zone
  -> Transformation Job
  -> Amazon S3 Silver Zone
  -> Data Quality Gate
  -> Amazon S3 Gold Zone
  -> Metadata Catalog
  -> API Layer
  -> Dashboard / BI
  -> AI Assistant
```

## Service Mapping

| Local Component | AWS Production Option | Purpose |
| --- | --- | --- |
| Docker Compose pipeline | AWS Glue, ECS Fargate task, AWS Batch, or MWAA | Run ingestion and transformation jobs |
| `data/raw/` | Amazon S3 Raw Zone | Store source-aligned immutable data |
| `data/silver/` | Amazon S3 Silver Zone | Store cleaned and enriched analytical data |
| `data/gold/` | Amazon S3 Gold Zone | Store reusable business data products |
| Parquet files | S3 Parquet datasets, optionally governed with Glue Data Catalog | Efficient analytical storage |
| Metadata JSON | AWS Glue Data Catalog or DynamoDB metadata table | Dataset discovery and governance |
| Data quality script | Glue Data Quality, Great Expectations, or custom validation job | Block bad data before publishing Gold products |
| FastAPI service | AWS App Runner, ECS Fargate, or Lambda with API Gateway | Serve data products as APIs |
| Streamlit dashboard | ECS Fargate, App Runner, or internal analytics portal | Business-facing consumption |
| Governed AI Agent | Bedrock or controlled LLM service grounded in Gold datasets | Natural-language product interface |
| Local logs | CloudWatch Logs and Metrics | Observability |
| Local config | SSM Parameter Store or Secrets Manager | Secure configuration and credentials |

## Migration Path

### Phase 1: Lift the Current Pipeline

Keep the Python scripts mostly unchanged and run them as containerized jobs.

Recommended AWS options:

- Build a Docker image for the pipeline.
- Push the image to Amazon ECR.
- Run the image with ECS Fargate, AWS Batch, or Glue Python jobs.
- Replace local `data/` paths with S3 paths.
- Keep Parquet as the storage format.

Goal:

Make the same MVP pipeline execute in AWS without redesigning the product logic.

### Phase 2: Add Managed Orchestration

Schedule and monitor the pipeline.

Recommended AWS options:

- Amazon MWAA if Airflow-style orchestration is required.
- EventBridge Scheduler for simple scheduled jobs.
- Step Functions for explicit workflow states and retries.

Airflow/MWAA is a production orchestration option, not part of the current local MVP.

Workflow:

```text
Ingest -> Build Silver -> Validate Quality -> Build Gold -> Build Metadata -> Publish APIs
```

Data quality should remain a blocking step. Gold datasets should only be published when critical checks pass.

### Phase 3: Add Catalog and Governance

Register datasets and make them discoverable.

Recommended AWS options:

- AWS Glue Data Catalog for table metadata.
- Lake Formation if access control by dataset, role, or consumer is required.
- S3 bucket policies and IAM roles for least-privilege access.

Governance outcomes:

- Raw, Silver, and Gold zones are clearly separated.
- Consumers can discover Gold products.
- Access can be controlled by product, user, or customer segment.
- Metadata supports auditability and commercial product management.

If the platform moves from file-based Parquet processing into a warehouse or lakehouse modeling layer, dbt could be introduced for SQL-based transformations, model lineage, tests, and documentation. That would be a production modeling evolution, not a current dependency.

### Phase 4: Serve Data Products

Expose Gold products through APIs and dashboards.

Recommended AWS options:

- FastAPI on ECS Fargate or App Runner.
- API Gateway for authentication, throttling, and external API management.
- CloudFront if public dashboard or API acceleration is needed.
- Cognito or IAM-based authentication depending on the customer model.

Commercial outcomes:

- API subscriptions can be metered and controlled.
- Different customers can receive different product access.
- Dashboards can be limited to internal analysts, premium customers, or business stakeholders.

### Phase 5: Add AI Product Layer

The current Governed AI Agent is deterministic and grounded in Gold datasets. In production, an LLM can be added without losing control of the data foundation.

Recommended AWS options:

- Amazon Bedrock for managed LLM access.
- Retrieval-augmented generation over Gold datasets and metadata.
- Guardrails that restrict answers to supported market intelligence topics.
- Prompt templates that require source dataset references.

Principle:

The LLM/RAG layer should improve language quality and user experience, but Gold datasets should remain the source of truth.

## Operational Readiness

Production operation should include:

- Job-level retry policies.
- Failure notifications through CloudWatch alarms or SNS.
- Data quality failure alerts.
- Dataset freshness checks.
- Row-count and schema-change monitoring.
- API latency and error-rate monitoring.
- Access logs for customer and product usage.
- Cost monitoring by storage, compute, and API usage.

## Security Considerations

The MVP does not require credentials because it uses public data. A production deployment should include:

- IAM roles with least privilege.
- Secrets Manager for credentials and API keys.
- S3 encryption at rest.
- TLS for API access.
- Private subnets for internal services where applicable.
- API authentication and rate limits.
- Customer entitlement checks for paid data products.

## Monetization Enablement

Cloud deployment enables commercial packaging:

- API keys and subscription tiers.
- Customer-specific access to Gold datasets.
- Usage metering by endpoint, customer, or product.
- Premium dashboards for different user groups.
- Scheduled executive reports.
- Alert products for unusual volume, volatility, and performance signals.
- AI assistant access as a premium interface over governed data products.

## Why AWS Migration Is Straightforward

The project is already structured around portable data engineering boundaries:

- Scripts are modular by pipeline stage.
- Data is stored in Parquet.
- Paths are centralized and can be adapted to S3.
- Docker Compose proves containerized execution.
- API and dashboard are separate runtime services.
- Gold products are already separated from Raw and Silver data.
- Data quality is an explicit pipeline step.

This means the main cloud work is infrastructure and operationalization, not rewriting the business logic.

## Suggested AWS MVP Architecture

For a first cloud version, a pragmatic setup would be:

```text
Amazon ECR
  -> ECS Fargate scheduled pipeline task
  -> S3 Raw/Silver/Gold buckets or prefixes
  -> Glue Data Catalog
  -> ECS/App Runner FastAPI service
  -> ECS/App Runner Streamlit dashboard
  -> CloudWatch monitoring
  -> Secrets Manager / SSM Parameter Store
```

This keeps the architecture understandable, production-oriented, and close to the current implementation.

## Future Enhancements

- Replace local generated metadata with Glue Catalog synchronization.
- Add partitioned S3 datasets by date and ticker.
- Add incremental ingestion instead of full refreshes.
- Add CI/CD for pipeline, API, and dashboard containers.
- Add customer authentication and entitlement management.
- Add API usage metering for commercial billing.
- Add Bedrock-based LLM/RAG narrative generation grounded in Gold datasets.
- Add data contracts and schema evolution policies.

## Product Roadmap Phases

| Phase | Focus | Description |
| --- | --- | --- |
| Phase 1: MVP current state | Market Intelligence foundation | Raw/Silver/Gold architecture, data quality, metadata, APIs, dashboard, deterministic agent, and LLM-governed assistant. |
| Phase 2: RAG and LLM enrichment | Natural-language intelligence | Add retrieval over licensed documents, issuer reports, metadata, and governed knowledge sources while keeping Gold datasets as source of truth. |
| Phase 3: Forecasting models | Advanced analytics research | Add Prophet, ARIMA, or LSTM experiments for forecasting use cases as a separate governed product line, not as current MVP behavior. |
| Phase 4: Anomaly detection | Monitoring and alerting | Detect unusual volume, volatility, liquidity, or operational data-quality events. |
| Phase 5: Personalized recommendations | Customer-specific experience | Recommend relevant dashboards, alerts, reports, or API products by role, entitlement, and workflow. This should not provide investment advice. |
