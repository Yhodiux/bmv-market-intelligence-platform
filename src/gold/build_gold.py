from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SILVER_PATH = PROJECT_ROOT / "data" / "silver" / "market_prices_silver.parquet"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "gold"

IDENTITY_COLUMNS = ["ticker", "issuer_name", "sector", "date"]


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def read_silver_prices(silver_path: Path) -> pd.DataFrame:
    if not silver_path.exists():
        raise FileNotFoundError(f"Silver market prices file not found: {silver_path}")

    silver = pd.read_parquet(silver_path)
    if silver.empty:
        raise ValueError(f"Silver market prices file is empty: {silver_path}")

    required_columns = {
        "date",
        "ticker",
        "issuer_name",
        "sector",
        "close_price",
        "adjusted_close",
        "volume",
        "daily_return",
        "trend_flag",
    }
    missing_columns = required_columns - set(silver.columns)
    if missing_columns:
        raise ValueError(f"Silver market prices missing columns: {sorted(missing_columns)}")

    silver = silver.copy()
    silver["date"] = pd.to_datetime(silver["date"])
    silver["ticker"] = silver["ticker"].astype("string")
    silver = silver.sort_values(["ticker", "date"]).reset_index(drop=True)

    for column in ["close_price", "adjusted_close", "volume", "daily_return"]:
        silver[column] = pd.to_numeric(silver[column], errors="coerce")

    return silver


def add_common_market_features(silver: pd.DataFrame) -> pd.DataFrame:
    enriched = silver.copy()
    grouped = enriched.groupby("ticker", group_keys=False)

    for window in [7, 30, 90]:
        enriched[f"return_{window}d"] = grouped["adjusted_close"].pct_change(periods=window)
        enriched[f"volatility_{window}d"] = grouped["daily_return"].rolling(window=window, min_periods=window).std().reset_index(
            level=0,
            drop=True,
        )

    enriched["avg_volume_30d"] = grouped["volume"].rolling(window=30, min_periods=1).mean().reset_index(level=0, drop=True)
    enriched["max_volume_30d"] = grouped["volume"].rolling(window=30, min_periods=1).max().reset_index(level=0, drop=True)
    enriched["min_volume_30d"] = grouped["volume"].rolling(window=30, min_periods=1).min().reset_index(level=0, drop=True)
    enriched["volume_variation_pct"] = (enriched["volume"] - enriched["avg_volume_30d"]) / enriched["avg_volume_30d"]
    enriched.loc[enriched["avg_volume_30d"] == 0, "volume_variation_pct"] = 0

    enriched["issuer_return_30d"] = enriched["return_30d"]
    enriched["sector_avg_return_30d"] = enriched.groupby(["sector", "date"])["issuer_return_30d"].transform("mean")
    enriched["sector_total_volume"] = enriched.groupby(["sector", "date"])["volume"].transform("sum")
    enriched["market_participation"] = enriched["volume"] / enriched["sector_total_volume"]
    enriched.loc[enriched["sector_total_volume"] == 0, "market_participation"] = 0
    enriched["trend_strength"] = (enriched["issuer_return_30d"] - enriched["sector_avg_return_30d"]).abs()

    return enriched


def categorize_performance(return_30d: pd.Series) -> pd.Series:
    category = pd.Series("Neutral", index=return_30d.index, dtype="string")
    category.loc[return_30d >= 0.05] = "Outperformer"
    category.loc[return_30d <= -0.05] = "Underperformer"
    return category


def categorize_risk(volatility_30d: pd.Series) -> pd.Series:
    category = pd.Series("Unknown", index=volatility_30d.index, dtype="string")
    valid = volatility_30d.dropna()
    if valid.empty:
        return category

    low_threshold = valid.quantile(0.33)
    high_threshold = valid.quantile(0.66)
    category.loc[volatility_30d <= low_threshold] = "Low"
    category.loc[(volatility_30d > low_threshold) & (volatility_30d <= high_threshold)] = "Medium"
    category.loc[volatility_30d > high_threshold] = "High"
    return category


def build_gold_performance(features: pd.DataFrame) -> pd.DataFrame:
    gold = features[IDENTITY_COLUMNS + ["return_7d", "return_30d", "return_90d"]].copy()
    gold["performance_rank_30d"] = gold.groupby("date")["return_30d"].rank(method="dense", ascending=False)
    gold["performance_category"] = categorize_performance(gold["return_30d"])
    return gold[
        IDENTITY_COLUMNS
        + [
            "return_7d",
            "return_30d",
            "return_90d",
            "performance_rank_30d",
            "performance_category",
        ]
    ]


def build_gold_volatility(features: pd.DataFrame) -> pd.DataFrame:
    gold = features[IDENTITY_COLUMNS + ["volatility_7d", "volatility_30d", "volatility_90d"]].copy()
    gold["risk_level"] = categorize_risk(gold["volatility_30d"])
    return gold[IDENTITY_COLUMNS + ["volatility_7d", "volatility_30d", "volatility_90d", "risk_level"]]


def build_gold_liquidity(features: pd.DataFrame) -> pd.DataFrame:
    gold = features[
        IDENTITY_COLUMNS
        + [
            "volume",
            "avg_volume_30d",
            "max_volume_30d",
            "min_volume_30d",
            "volume_variation_pct",
        ]
    ].copy()
    gold["liquidity_score"] = gold.groupby("date")["avg_volume_30d"].rank(pct=True) * 100
    gold["liquidity_rank"] = gold.groupby("date")["liquidity_score"].rank(method="dense", ascending=False)
    return gold[
        IDENTITY_COLUMNS
        + [
            "volume",
            "avg_volume_30d",
            "max_volume_30d",
            "min_volume_30d",
            "volume_variation_pct",
            "liquidity_score",
            "liquidity_rank",
        ]
    ]


def build_gold_market_trends(features: pd.DataFrame) -> pd.DataFrame:
    return features[
        IDENTITY_COLUMNS
        + [
            "trend_flag",
            "sector_avg_return_30d",
            "issuer_return_30d",
            "market_participation",
            "trend_strength",
        ]
    ].copy()


def severity_from_row(row: pd.Series) -> str:
    return_30d = row["return_30d"]
    volatility_30d = row["volatility_30d"]
    volume_variation_pct = row["volume_variation_pct"]

    if pd.notna(return_30d) and return_30d <= -0.08:
        return "High"
    if pd.notna(volatility_30d) and row["risk_level"] == "High":
        return "Medium"
    if pd.notna(volume_variation_pct) and abs(volume_variation_pct) >= 0.5:
        return "Medium"
    return "Low"


def insight_from_row(row: pd.Series) -> pd.Series:
    issuer = row["issuer_name"]
    ticker = row["ticker"]
    return_30d = row["return_30d"]
    risk_level = row["risk_level"]
    volume_variation_pct = row["volume_variation_pct"]

    if pd.notna(return_30d) and return_30d >= 0.05:
        title = f"{ticker} shows positive 30-day momentum"
        summary = f"{issuer} recorded a 30-day return of {return_30d:.2%}."
        interpretation = "The issuer may be gaining relative market preference over the recent trading window."
        question = f"What drivers explain the positive 30-day performance for {ticker}?"
    elif pd.notna(return_30d) and return_30d <= -0.05:
        title = f"{ticker} shows negative 30-day pressure"
        summary = f"{issuer} recorded a 30-day return of {return_30d:.2%}."
        interpretation = "The issuer may require closer monitoring due to recent price deterioration."
        question = f"Is the negative 30-day return for {ticker} sector-wide or issuer-specific?"
    elif risk_level == "High":
        title = f"{ticker} has elevated volatility"
        summary = f"{issuer} is classified as High risk based on 30-day volatility."
        interpretation = "The issuer may be less suitable for low-risk data product audiences."
        question = f"How does {ticker} volatility compare with peers in its sector?"
    elif pd.notna(volume_variation_pct) and abs(volume_variation_pct) >= 0.5:
        title = f"{ticker} shows unusual volume behavior"
        summary = f"{issuer} volume differs from its 30-day average by {volume_variation_pct:.2%}."
        interpretation = "Trading activity may indicate a change in market attention or participation."
        question = f"What events may explain the unusual volume behavior for {ticker}?"
    else:
        title = f"{ticker} remains stable"
        summary = f"{issuer} does not show extreme 30-day performance, volatility, or volume signals."
        interpretation = "The issuer can serve as a baseline comparison in market intelligence products."
        question = f"What makes {ticker} stable relative to other issuers?"

    return pd.Series(
        {
            "insight_title": title,
            "insight_summary": summary,
            "business_interpretation": interpretation,
            "recommended_question": question,
        }
    )


def build_gold_ai_insights(features: pd.DataFrame, volatility: pd.DataFrame) -> pd.DataFrame:
    latest_date = features["date"].max()
    latest = features.loc[features["date"] == latest_date].copy()
    latest = latest.merge(
        volatility[["ticker", "date", "risk_level"]],
        on=["ticker", "date"],
        how="left",
        validate="one_to_one",
    )

    insight_columns = latest.apply(insight_from_row, axis=1)
    latest = pd.concat([latest, insight_columns], axis=1)
    latest["severity"] = latest.apply(severity_from_row, axis=1)

    return latest[
        IDENTITY_COLUMNS
        + [
            "insight_title",
            "insight_summary",
            "business_interpretation",
            "recommended_question",
            "severity",
        ]
    ].sort_values(["severity", "ticker"], ascending=[True, True])


def write_dataset(data: pd.DataFrame, output_dir: Path, dataset_name: str) -> Path:
    if data.empty:
        raise ValueError(f"{dataset_name} dataset is empty.")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{dataset_name}.parquet"
    data.to_parquet(output_path, index=False)
    logging.info("Wrote %s rows to %s", len(data), output_path)
    return output_path


def run_gold_build(silver_path: Path, output_dir: Path) -> list[Path]:
    silver = read_silver_prices(silver_path)
    features = add_common_market_features(silver)

    performance = build_gold_performance(features)
    volatility = build_gold_volatility(features)
    liquidity = build_gold_liquidity(features)
    market_trends = build_gold_market_trends(features)
    ai_insights = build_gold_ai_insights(features, volatility)

    datasets = {
        "gold_performance": performance,
        "gold_volatility": volatility,
        "gold_liquidity": liquidity,
        "gold_market_trends": market_trends,
        "gold_ai_insights": ai_insights,
    }

    return [write_dataset(data, output_dir, name) for name, data in datasets.items()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Gold market intelligence data products.")
    parser.add_argument(
        "--silver-path",
        type=Path,
        default=DEFAULT_SILVER_PATH,
        help="Path to the silver market prices parquet file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where gold parquet files will be written.",
    )
    return parser.parse_args()


def main() -> None:
    configure_logging()
    args = parse_args()
    output_paths = run_gold_build(args.silver_path, args.output_dir)
    logging.info("Gold build completed successfully: %s", ", ".join(str(path) for path in output_paths))


if __name__ == "__main__":
    main()
