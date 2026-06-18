# Future AWS Architecture

## Current MVP Architecture

The current MVP runs as a local, reproducible environment using Docker. It demonstrates the full market intelligence flow without requiring cloud infrastructure, paid data feeds, or enterprise platform dependencies.

The local architecture includes:

- Local Docker environment for reproducible execution.
- Data ingestion from public market data sources.
- Raw and transformed datasets stored as local Parquet files.
- Gold datasets for performance, volatility, liquidity, market trends, and AI-ready insights.
- FastAPI service exposing governed data products.
- Streamlit dashboard for business consumption.
- AI Market Intelligence Agent for governed natural-language access to Gold data products.

This MVP validates the product logic: market observations can be transformed into governed data products and consumed through APIs, dashboards, and AI-enabled services.

## Future AWS Architecture

The same product architecture can evolve into an enterprise AWS architecture by replacing local runtime components with managed cloud services.

```text
Sources
  |
  v
Glue ETL
  |
  v
S3 Raw
  |
  v
S3 Silver
  |
  v
Data Quality
  |
  v
S3 Gold
  |
  v
Glue Data Catalog
  |
  v
Athena
  |
  v
API Layer
  |
  v
AI Services
  |
  v
Business Consumers
```

In this target architecture, AWS provides the foundation for orchestration, scalable storage, data governance, analytical query access, API distribution, and managed AI service integration.

## AWS Services Mapping

| Current Component | Future AWS Service |
| --- | --- |
| Python ETL scripts | AWS Glue |
| Local Parquet files | Amazon S3 |
| Raw data folder | S3 Raw zone |
| Silver data folder | S3 Silver zone |
| Gold data folder | S3 Gold zone |
| Data quality validation scripts | AWS Glue Data Quality or AWS Deequ-based validation |
| Metadata JSON files | AWS Glue Data Catalog |
| Local analytical reads | Amazon Athena |
| FastAPI service | Amazon ECS Fargate or AWS Lambda with Amazon API Gateway |
| Streamlit dashboard | Amazon QuickSight or Tableau |
| OpenAI API integration | Amazon Bedrock or enterprise LLM services |
| `.env` secrets | AWS Secrets Manager |
| Docker Compose runtime | Amazon ECS, AWS Batch, or orchestrated Glue jobs |
| Local logs | Amazon CloudWatch |
| Local access control assumptions | IAM, API Gateway authorizers, and enterprise identity integration |

## AI Services Layer

The LLM provider is interchangeable.

The architecture should not depend on a single model vendor as the source of business value. The value resides in the governed Gold data products: curated, documented, quality-controlled market intelligence datasets that can support multiple consumption channels.

The AI layer can use different providers depending on enterprise standards, security requirements, cost, latency, and deployment model:

- Amazon Bedrock
- OpenAI
- Azure OpenAI
- Anthropic Claude
- Internal enterprise models

In all cases, the AI service should operate as a controlled interface over governed data products. It should retrieve or receive structured evidence from the Gold layer, generate explanations within a defined market intelligence scope, and avoid unsupported predictions, price targets, or investment recommendations.

This design keeps the enterprise architecture flexible. Models can change, but the data products, contracts, governance rules, and monetization channels remain stable.

## Enterprise Vision

The future AWS architecture enables a stock exchange to operate market intelligence as an enterprise data product platform.

APIs, dashboards, reports, and AI services become multiple monetization channels built on top of the same governed Gold data products. This allows the organization to serve external customers such as brokers, fintechs, data vendors, institutional investors, and research teams, while also supporting internal commercial, issuer relations, analytics, and executive teams.

The strategic objective is not to build a market prediction engine. The objective is to create a governed information business: trusted market observations transformed into reusable data products, distributed through scalable services, and monetized through enterprise-grade channels.
