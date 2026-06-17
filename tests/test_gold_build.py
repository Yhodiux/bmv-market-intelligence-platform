from pathlib import Path

import pandas as pd

from src.gold.build_gold import DEFAULT_SILVER_PATH, run_gold_build


EXPECTED_GOLD_COLUMNS = {
    "gold_performance": {
        "ticker",
        "issuer_name",
        "sector",
        "date",
        "return_7d",
        "return_30d",
        "return_90d",
        "performance_rank_30d",
        "performance_category",
    },
    "gold_volatility": {
        "ticker",
        "issuer_name",
        "sector",
        "date",
        "volatility_7d",
        "volatility_30d",
        "volatility_90d",
        "risk_level",
    },
    "gold_liquidity": {
        "ticker",
        "issuer_name",
        "sector",
        "date",
        "volume",
        "avg_volume_30d",
        "max_volume_30d",
        "min_volume_30d",
        "volume_variation_pct",
        "liquidity_score",
        "liquidity_rank",
    },
    "gold_market_trends": {
        "ticker",
        "issuer_name",
        "sector",
        "date",
        "trend_flag",
        "sector_avg_return_30d",
        "issuer_return_30d",
        "market_participation",
        "trend_strength",
    },
    "gold_ai_insights": {
        "ticker",
        "issuer_name",
        "sector",
        "date",
        "insight_title",
        "insight_summary",
        "business_interpretation",
        "recommended_question",
        "severity",
    },
}


def test_gold_build_writes_expected_datasets(tmp_path: Path) -> None:
    output_paths = run_gold_build(DEFAULT_SILVER_PATH, tmp_path)

    assert len(output_paths) == 5
    assert {path.stem for path in output_paths} == set(EXPECTED_GOLD_COLUMNS)

    silver = pd.read_parquet(DEFAULT_SILVER_PATH)
    latest_issuer_count = silver.loc[
        pd.to_datetime(silver["date"]) == pd.to_datetime(silver["date"]).max(),
        "ticker",
    ].nunique()

    for dataset_name, expected_columns in EXPECTED_GOLD_COLUMNS.items():
        dataset = pd.read_parquet(tmp_path / f"{dataset_name}.parquet")

        assert not dataset.empty
        assert expected_columns.issubset(dataset.columns)

        if dataset_name == "gold_ai_insights":
            assert len(dataset) == latest_issuer_count
        else:
            assert len(dataset) == len(silver)
