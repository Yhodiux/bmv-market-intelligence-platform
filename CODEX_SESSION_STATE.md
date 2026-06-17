# Codex Session State

## Current Status

The project currently implements the local Raw and Silver layers for the BMV Market Intelligence Platform MVP.

## Implemented

- Docker Compose pipeline service.
- Yahoo Finance ingestion script.
- Ticker configuration with Mexican market issuers.
- Raw Parquet output under `data/raw/`.
- Silver transformation script.
- Silver Parquet output under `data/silver/`.

## Important Adjustments Made

- Updated `yfinance` from `0.2.50` to `1.4.1` because the older version failed with `JSONDecodeError` against Yahoo Finance.
- Replaced `AMXL.MX` with `AMXB.MX` because `AMXL.MX` returned no Yahoo Finance data, while `AMXB.MX` worked.
- Updated ingestion normalization to handle the `MultiIndex` columns returned by newer `yfinance` versions.

## Key Files

- `README.md`
- `docker-compose.yml`
- `requirements.txt`
- `config/tickers.json`
- `src/ingestion/ingest_yfinance.py`
- `src/transformation/build_silver.py`
- `data/raw/market_prices_raw.parquet`
- `data/silver/market_prices_silver.parquet`

## Reproduce Current Pipeline

```bash
docker compose run --rm pipeline
```

The pipeline now executes:

1. `python src/ingestion/ingest_yfinance.py`
2. `python src/transformation/build_silver.py`

## Last Successful Validation

The latest successful pipeline run generated:

- Raw dataset: `data/raw/market_prices_raw.parquet`
- Silver dataset: `data/silver/market_prices_silver.parquet`
- Row count: `12,570` rows in both Raw and Silver
- Silver columns: `16`
- No null values in the expected Silver columns

Silver derived fields include:

- `daily_return`
- `intraday_volatility`
- `price_range`
- `volume_category`
- `trend_flag`
- `issuer_name`
- `sector`
- `ingestion_timestamp`

## Notes

Git may report `dubious ownership` in this environment. For Git inspection commands, use:

```bash
git -c safe.directory=F:/Proyectos/bmv-market-intelligence-platform status --short
```

The repository currently appears mostly untracked from Git's perspective in this environment, so avoid assuming a clean baseline.

## Recommended Next Step

Implement Data Quality:

- Validate Raw row count greater than zero.
- Validate Silver row count greater than zero.
- Check no null `ticker`.
- Check no null `date`.
- Check no duplicate `ticker` + `date`.
- Check prices are greater than or equal to zero.
- Check volume is greater than or equal to zero.
- Check `high_price >= low_price`.
- Check `close_price` is between `low_price` and `high_price` when possible.
- Write report to `data/metadata/data_quality_report.json`.
