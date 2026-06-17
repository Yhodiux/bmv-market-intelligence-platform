# BMV Market Intelligence Platform

Local data engineering MVP for Mexican market intelligence data products.

## Run pipeline

This first step downloads daily historical prices from Yahoo Finance, writes raw Parquet files under `data/raw/`, and builds the standardized Silver dataset under `data/silver/`.

```bash
docker compose run --rm pipeline
```

The pipeline uses the ticker universe defined in `config/tickers.json`.
