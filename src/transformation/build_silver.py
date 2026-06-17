from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "tickers.json"
DEFAULT_RAW_PATH = PROJECT_ROOT / "data" / "raw" / "market_prices_raw.parquet"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "silver"

SILVER_COLUMNS = [
    "date",
    "ticker",
    "open_price",
    "high_price",
    "low_price",
    "close_price",
    "adjusted_close",
    "volume",
    "daily_return",
    "intraday_volatility",
    "price_range",
    "volume_category",
    "trend_flag",
    "issuer_name",
    "sector",
    "ingestion_timestamp",
]


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def load_ticker_metadata(config_path: Path) -> pd.DataFrame:
    if not config_path.exists():
        raise FileNotFoundError(f"Ticker config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as file:
        config: dict[str, Any] = json.load(file)

    tickers = config.get("tickers", [])
    if not tickers:
        raise ValueError("Ticker config must include at least one ticker.")

    metadata = pd.DataFrame(tickers)
    required_columns = {"ticker", "issuer_name", "sector"}
    missing_columns = required_columns - set(metadata.columns)
    if missing_columns:
        raise ValueError(f"Ticker config missing columns: {sorted(missing_columns)}")

    return metadata[list(required_columns)]


def read_raw_prices(raw_path: Path) -> pd.DataFrame:
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw market prices file not found: {raw_path}")

    raw = pd.read_parquet(raw_path)
    if raw.empty:
        raise ValueError(f"Raw market prices file is empty: {raw_path}")

    required_columns = {"date", "ticker", "open", "high", "low", "close", "adj_close", "volume"}
    missing_columns = required_columns - set(raw.columns)
    if missing_columns:
        raise ValueError(f"Raw market prices missing columns: {sorted(missing_columns)}")

    return raw


def assign_volume_category(series: pd.Series) -> pd.Series:
    if series.nunique(dropna=True) < 3:
        return pd.Series("Medium", index=series.index, dtype="string")

    ranked = series.rank(method="first")
    return pd.qcut(
        ranked,
        q=3,
        labels=["Low", "Medium", "High"],
    ).astype("string")


def build_silver(raw: pd.DataFrame, metadata: pd.DataFrame) -> pd.DataFrame:
    silver = raw.rename(
        columns={
            "open": "open_price",
            "high": "high_price",
            "low": "low_price",
            "close": "close_price",
            "adj_close": "adjusted_close",
        }
    ).copy()

    silver["date"] = pd.to_datetime(silver["date"]).dt.date
    silver["ticker"] = silver["ticker"].astype("string")

    numeric_columns = [
        "open_price",
        "high_price",
        "low_price",
        "close_price",
        "adjusted_close",
        "volume",
    ]
    for column in numeric_columns:
        silver[column] = pd.to_numeric(silver[column], errors="coerce")

    silver = silver.sort_values(["ticker", "date"]).reset_index(drop=True)

    silver["daily_return"] = (silver["close_price"] - silver["open_price"]) / silver["open_price"]
    silver["intraday_volatility"] = (silver["high_price"] - silver["low_price"]) / silver["open_price"]
    silver["price_range"] = silver["high_price"] - silver["low_price"]
    silver["trend_flag"] = "Neutral"
    silver.loc[silver["daily_return"] > 0, "trend_flag"] = "Bullish"
    silver.loc[silver["daily_return"] < 0, "trend_flag"] = "Bearish"
    silver["volume_category"] = silver.groupby("ticker", group_keys=False)["volume"].apply(assign_volume_category)

    enriched = silver.merge(metadata, on="ticker", how="left", validate="many_to_one")
    missing_metadata = enriched.loc[enriched["issuer_name"].isna(), "ticker"].drop_duplicates().tolist()
    if missing_metadata:
        raise ValueError(f"Missing issuer metadata for tickers: {', '.join(missing_metadata)}")

    enriched["ingestion_timestamp"] = pd.Timestamp.utcnow().isoformat()

    return enriched[SILVER_COLUMNS]


def write_silver_output(silver: pd.DataFrame, output_dir: Path) -> Path:
    if silver.empty:
        raise ValueError("Silver dataset is empty.")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "market_prices_silver.parquet"
    silver.to_parquet(output_path, index=False)
    logging.info("Wrote %s rows to %s", len(silver), output_path)
    return output_path


def run_transformation(raw_path: Path, config_path: Path, output_dir: Path) -> Path:
    raw = read_raw_prices(raw_path)
    metadata = load_ticker_metadata(config_path)
    silver = build_silver(raw, metadata)
    return write_silver_output(silver, output_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Silver market prices dataset.")
    parser.add_argument(
        "--raw-path",
        type=Path,
        default=DEFAULT_RAW_PATH,
        help="Path to the raw market prices parquet file.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to ticker configuration JSON.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where silver parquet files will be written.",
    )
    return parser.parse_args()


def main() -> None:
    configure_logging()
    args = parse_args()
    output_path = run_transformation(args.raw_path, args.config, args.output_dir)
    logging.info("Silver transformation completed successfully: %s", output_path)


if __name__ == "__main__":
    main()
