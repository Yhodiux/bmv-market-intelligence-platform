from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "tickers.json"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "raw"

RAW_COLUMNS = [
    "date",
    "ticker",
    "open",
    "high",
    "low",
    "close",
    "adj_close",
    "volume",
]


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def load_config(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        raise FileNotFoundError(f"Ticker config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as file:
        config = json.load(file)

    tickers = config.get("tickers", [])
    if not tickers:
        raise ValueError("Ticker config must include at least one ticker.")

    return config


def normalize_yfinance_data(data: pd.DataFrame, ticker: str) -> pd.DataFrame:
    if data.empty:
        raise ValueError(f"No data returned for ticker {ticker}")

    if isinstance(data.columns, pd.MultiIndex):
        data = data.droplevel("Ticker", axis=1)

    normalized = (
        data.reset_index()
        .rename(
            columns={
                "Date": "date",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Adj Close": "adj_close",
                "Volume": "volume",
            }
        )
        .assign(ticker=ticker)
    )

    normalized["date"] = pd.to_datetime(normalized["date"]).dt.date

    missing_columns = set(RAW_COLUMNS) - set(normalized.columns)
    if missing_columns:
        raise ValueError(f"Missing expected columns for {ticker}: {sorted(missing_columns)}")

    return normalized[RAW_COLUMNS]


def download_ticker(ticker: str, period: str, interval: str) -> pd.DataFrame:
    logging.info("Downloading %s data with period=%s interval=%s", ticker, period, interval)
    data = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=False,
        progress=False,
        threads=False,
    )
    return normalize_yfinance_data(data, ticker)


def write_raw_outputs(raw_frames: list[pd.DataFrame], output_dir: Path) -> Path:
    if not raw_frames:
        raise ValueError("No raw data frames were created.")

    output_dir.mkdir(parents=True, exist_ok=True)
    combined = pd.concat(raw_frames, ignore_index=True)

    if combined.empty:
        raise ValueError("Combined raw dataset is empty.")

    for ticker, ticker_data in combined.groupby("ticker"):
        safe_ticker = ticker.replace(".", "_")
        ticker_path = output_dir / f"{safe_ticker}.parquet"
        ticker_data.to_parquet(ticker_path, index=False)
        logging.info("Wrote %s rows to %s", len(ticker_data), ticker_path)

    combined_path = output_dir / "market_prices_raw.parquet"
    combined.to_parquet(combined_path, index=False)
    logging.info("Wrote %s total rows to %s", len(combined), combined_path)

    return combined_path


def run_ingestion(config_path: Path, output_dir: Path) -> Path:
    config = load_config(config_path)
    period = config.get("period", "5y")
    interval = config.get("interval", "1d")

    raw_frames: list[pd.DataFrame] = []
    failed_tickers: list[str] = []

    for item in config["tickers"]:
        ticker = item["ticker"]
        try:
            raw_frames.append(download_ticker(ticker, period, interval))
        except Exception:
            failed_tickers.append(ticker)
            logging.exception("Failed to ingest ticker %s", ticker)

    if failed_tickers:
        raise RuntimeError(f"Failed to ingest tickers: {', '.join(failed_tickers)}")

    return write_raw_outputs(raw_frames, output_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest Mexican market data from Yahoo Finance.")
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
        help="Directory where raw parquet files will be written.",
    )
    return parser.parse_args()


def main() -> None:
    configure_logging()
    args = parse_args()
    output_path = run_ingestion(args.config, args.output_dir)
    logging.info("Raw ingestion completed successfully: %s", output_path)


if __name__ == "__main__":
    main()
