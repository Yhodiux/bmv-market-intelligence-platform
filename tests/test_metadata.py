from src.metadata.build_metadata import build_metadata


def test_metadata_catalog_describes_all_current_datasets() -> None:
    metadata = build_metadata()

    dataset_names = {dataset["dataset_name"] for dataset in metadata["datasets"]}

    assert metadata["dataset_count"] == 7
    assert dataset_names == {
        "market_prices_raw",
        "market_prices_silver",
        "gold_performance",
        "gold_volatility",
        "gold_liquidity",
        "gold_market_trends",
        "gold_ai_insights",
    }

    for dataset in metadata["datasets"]:
        assert dataset["record_count"] > 0
        assert dataset["column_count"] == len(dataset["columns"])
        assert dataset["business_description"]
        assert dataset["source"]
