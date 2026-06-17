from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from src.ai_agent.market_agent import answer_question


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
METADATA_PATH = DATA_DIR / "metadata" / "datasets_metadata.json"

DATASET_PATHS = {
    "performance": DATA_DIR / "gold" / "gold_performance.parquet",
    "volatility": DATA_DIR / "gold" / "gold_volatility.parquet",
    "liquidity": DATA_DIR / "gold" / "gold_liquidity.parquet",
    "market-trends": DATA_DIR / "gold" / "gold_market_trends.parquet",
    "ai-insights": DATA_DIR / "gold" / "gold_ai_insights.parquet",
}

app = FastAPI(
    title="BMV Market Intelligence API",
    description="Local API exposing BMV market intelligence Gold data products.",
    version="0.1.0",
)


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


def read_parquet_dataset(dataset_key: str) -> pd.DataFrame:
    path = DATASET_PATHS[dataset_key]
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Dataset file not found: {path}")
    return pd.read_parquet(path)


def serialize_records(data: pd.DataFrame) -> list[dict[str, Any]]:
    cleaned = data.copy()
    for column in cleaned.columns:
        if pd.api.types.is_datetime64_any_dtype(cleaned[column]):
            cleaned[column] = cleaned[column].dt.strftime("%Y-%m-%d")

    cleaned = cleaned.where(pd.notna(cleaned), None)
    return cleaned.to_dict(orient="records")


def filter_dataset(data: pd.DataFrame, ticker: str | None, limit: int) -> list[dict[str, Any]]:
    if ticker:
        data = data.loc[data["ticker"].astype(str).str.upper() == ticker.upper()]

    if "date" in data.columns:
        data = data.sort_values("date", ascending=False)

    return serialize_records(data.head(limit))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/datasets")
def datasets() -> dict[str, Any]:
    if not METADATA_PATH.exists():
        raise HTTPException(status_code=404, detail=f"Metadata file not found: {METADATA_PATH}")

    with METADATA_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


@app.get("/performance")
def performance(
    ticker: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
) -> list[dict[str, Any]]:
    return filter_dataset(read_parquet_dataset("performance"), ticker, limit)


@app.get("/volatility")
def volatility(
    ticker: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
) -> list[dict[str, Any]]:
    return filter_dataset(read_parquet_dataset("volatility"), ticker, limit)


@app.get("/liquidity")
def liquidity(
    ticker: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
) -> list[dict[str, Any]]:
    return filter_dataset(read_parquet_dataset("liquidity"), ticker, limit)


@app.get("/market-trends")
def market_trends(
    ticker: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
) -> list[dict[str, Any]]:
    return filter_dataset(read_parquet_dataset("market-trends"), ticker, limit)


@app.get("/ai-insights")
def ai_insights(
    ticker: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
) -> list[dict[str, Any]]:
    return filter_dataset(read_parquet_dataset("ai-insights"), ticker, limit)


@app.post("/ask")
def ask(request: AskRequest) -> dict[str, Any]:
    try:
        return answer_question(request.question)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
