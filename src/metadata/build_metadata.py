from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "data" / "metadata" / "datasets_metadata.json"

DATASETS = [
    {
        "dataset_name": "market_prices_raw",
        "layer": "raw",
        "path": PROJECT_ROOT / "data" / "raw" / "market_prices_raw.parquet",
        "source": "Yahoo Finance via yfinance",
        "business_description": "Historical daily market prices preserving the source market data structure.",
    },
    {
        "dataset_name": "market_prices_silver",
        "layer": "silver",
        "path": PROJECT_ROOT / "data" / "silver" / "market_prices_silver.parquet",
        "source": "Raw market prices and ticker metadata",
        "business_description": "Cleaned, standardized, and enriched market prices ready for data products.",
    },
    {
        "dataset_name": "gold_performance",
        "layer": "gold",
        "path": PROJECT_ROOT / "data" / "gold" / "gold_performance.parquet",
        "source": "Silver market prices",
        "business_description": "Issuer performance product with 7, 30, and 90 day returns and rankings.",
    },
    {
        "dataset_name": "gold_volatility",
        "layer": "gold",
        "path": PROJECT_ROOT / "data" / "gold" / "gold_volatility.parquet",
        "source": "Silver market prices",
        "business_description": "Risk product with rolling volatility metrics and risk levels.",
    },
    {
        "dataset_name": "gold_liquidity",
        "layer": "gold",
        "path": PROJECT_ROOT / "data" / "gold" / "gold_liquidity.parquet",
        "source": "Silver market prices",
        "business_description": "Liquidity product with volume windows, variation, score, and rank.",
    },
    {
        "dataset_name": "gold_market_trends",
        "layer": "gold",
        "path": PROJECT_ROOT / "data" / "gold" / "gold_market_trends.parquet",
        "source": "Silver market prices",
        "business_description": "Trend product comparing issuer movement, sector returns, and participation.",
    },
    {
        "dataset_name": "gold_ai_insights",
        "layer": "gold",
        "path": PROJECT_ROOT / "data" / "gold" / "gold_ai_insights.parquet",
        "source": "Gold market intelligence signals",
        "business_description": "AI-ready market insight prompts and interpretations grounded in Gold datasets.",
    },
]


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def build_dataset_metadata(dataset: dict[str, Any]) -> dict[str, Any]:
    path = Path(dataset["path"])
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {path}")

    data = pd.read_parquet(path)
    return {
        "dataset_name": dataset["dataset_name"],
        "layer": dataset["layer"],
        "record_count": len(data),
        "column_count": len(data.columns),
        "columns": list(data.columns),
        "created_at": pd.Timestamp.utcnow().isoformat(),
        "source": dataset["source"],
        "business_description": dataset["business_description"],
        "path": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
    }


def build_metadata() -> dict[str, Any]:
    datasets = [build_dataset_metadata(dataset) for dataset in DATASETS]
    return {
        "generated_at": pd.Timestamp.utcnow().isoformat(),
        "dataset_count": len(datasets),
        "datasets": datasets,
    }


def write_metadata(metadata: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2, ensure_ascii=True, default=str)
        file.write("\n")

    logging.info("Wrote dataset metadata to %s", output_path)
    return output_path


def run_metadata_build(output_path: Path) -> Path:
    metadata = build_metadata()
    return write_metadata(metadata, output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build dataset metadata catalog.")
    parser.add_argument(
        "--output-path",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Path where dataset metadata JSON will be written.",
    )
    return parser.parse_args()


def main() -> None:
    configure_logging()
    args = parse_args()
    output_path = run_metadata_build(args.output_path)
    logging.info("Metadata build completed successfully: %s", output_path)


if __name__ == "__main__":
    main()
