from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"

DATASET_PATHS = {
    "gold_performance": DATA_DIR / "gold" / "gold_performance.parquet",
    "gold_volatility": DATA_DIR / "gold" / "gold_volatility.parquet",
    "gold_liquidity": DATA_DIR / "gold" / "gold_liquidity.parquet",
    "gold_market_trends": DATA_DIR / "gold" / "gold_market_trends.parquet",
    "gold_ai_insights": DATA_DIR / "gold" / "gold_ai_insights.parquet",
}

SUPPORTED_QUESTIONS = [
    "Which issuers had the best 30-day performance?",
    "Which issuers show sustained growth with controlled volatility?",
    "Which sectors show higher volatility?",
    "Which companies show unusual volume behavior?",
    "What are the most relevant market insights?",
]


@dataclass(frozen=True)
class AgentResponse:
    question: str
    answer: str
    data_points: list[dict[str, Any]]
    source_datasets: list[str]
    supported_questions: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "answer": self.answer,
            "data_points": self.data_points,
            "source_datasets": self.source_datasets,
            "supported_questions": self.supported_questions,
        }


def read_dataset(dataset_name: str) -> pd.DataFrame:
    path = DATASET_PATHS[dataset_name]
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {path}")

    data = pd.read_parquet(path)
    if data.empty:
        raise ValueError(f"Dataset is empty: {path}")

    if "date" in data.columns:
        data["date"] = pd.to_datetime(data["date"])

    return data


def latest_snapshot(data: pd.DataFrame) -> pd.DataFrame:
    if "date" not in data.columns:
        return data.copy()

    latest_date = data["date"].max()
    return data.loc[data["date"] == latest_date].copy()


def serialize_records(data: pd.DataFrame) -> list[dict[str, Any]]:
    cleaned = data.copy()
    for column in cleaned.columns:
        if pd.api.types.is_datetime64_any_dtype(cleaned[column]):
            cleaned[column] = cleaned[column].dt.strftime("%Y-%m-%d")

    cleaned = cleaned.where(pd.notna(cleaned), None)
    return cleaned.to_dict(orient="records")


def detect_intent(question: str) -> str:
    normalized = question.lower()

    if any(term in normalized for term in ["best", "top", "performance", "rendimiento", "mejor"]):
        return "best_performance"

    if any(term in normalized for term in ["sustained", "growth", "controlled", "crecimiento", "controlada"]):
        return "controlled_growth"

    if any(term in normalized for term in ["sector", "volatility", "volatilidad", "risk", "riesgo"]):
        return "sector_volatility"

    if any(term in normalized for term in ["volume", "volumen", "liquidity", "liquidez", "unusual", "inusual"]):
        return "unusual_volume"

    if any(term in normalized for term in ["insight", "insights", "relevant", "relevante"]):
        return "market_insights"

    return "unsupported"


def answer_best_performance(question: str) -> AgentResponse:
    performance = latest_snapshot(read_dataset("gold_performance"))
    result = (
        performance.dropna(subset=["return_30d"])
        .sort_values(["return_30d", "performance_rank_30d"], ascending=[False, True])
        .head(5)
    )

    records = serialize_records(
        result[
            [
                "date",
                "ticker",
                "issuer_name",
                "sector",
                "return_30d",
                "performance_rank_30d",
                "performance_category",
            ]
        ]
    )
    answer = "The strongest 30-day performers are ranked using the latest Gold performance snapshot."
    return AgentResponse(question, answer, records, ["gold_performance"], SUPPORTED_QUESTIONS)


def answer_controlled_growth(question: str) -> AgentResponse:
    performance = latest_snapshot(read_dataset("gold_performance"))
    volatility = latest_snapshot(read_dataset("gold_volatility"))
    merged = performance.merge(
        volatility[["ticker", "date", "volatility_30d", "risk_level"]],
        on=["ticker", "date"],
        how="inner",
        validate="one_to_one",
    )

    candidates = merged.loc[
        (merged["return_30d"] > 0)
        & (merged["return_90d"] > 0)
        & (merged["risk_level"].isin(["Low", "Medium"]))
    ]
    result = candidates.sort_values(["return_30d", "volatility_30d"], ascending=[False, True]).head(5)

    records = serialize_records(
        result[
            [
                "date",
                "ticker",
                "issuer_name",
                "sector",
                "return_30d",
                "return_90d",
                "volatility_30d",
                "risk_level",
            ]
        ]
    )

    answer = (
        "Issuers with sustained growth and controlled volatility are selected when both 30-day and "
        "90-day returns are positive and 30-day risk is Low or Medium."
    )
    return AgentResponse(question, answer, records, ["gold_performance", "gold_volatility"], SUPPORTED_QUESTIONS)


def answer_sector_volatility(question: str) -> AgentResponse:
    volatility = latest_snapshot(read_dataset("gold_volatility"))
    sector_risk = (
        volatility.dropna(subset=["volatility_30d"])
        .groupby("sector", as_index=False)
        .agg(
            avg_volatility_30d=("volatility_30d", "mean"),
            max_volatility_30d=("volatility_30d", "max"),
            issuer_count=("ticker", "nunique"),
        )
        .sort_values("avg_volatility_30d", ascending=False)
    )

    records = serialize_records(sector_risk.head(5))
    answer = "Sectors with higher volatility are ranked by average 30-day volatility in the latest snapshot."
    return AgentResponse(question, answer, records, ["gold_volatility"], SUPPORTED_QUESTIONS)


def answer_unusual_volume(question: str) -> AgentResponse:
    liquidity = latest_snapshot(read_dataset("gold_liquidity"))
    liquidity["absolute_volume_variation_pct"] = liquidity["volume_variation_pct"].abs()
    result = liquidity.sort_values("absolute_volume_variation_pct", ascending=False).head(5)

    records = serialize_records(
        result[
            [
                "date",
                "ticker",
                "issuer_name",
                "sector",
                "volume",
                "avg_volume_30d",
                "volume_variation_pct",
                "liquidity_score",
                "liquidity_rank",
            ]
        ]
    )
    answer = "Unusual volume behavior is ranked by absolute variation versus the issuer's 30-day average volume."
    return AgentResponse(question, answer, records, ["gold_liquidity"], SUPPORTED_QUESTIONS)


def answer_market_insights(question: str) -> AgentResponse:
    insights = read_dataset("gold_ai_insights")
    severity_order = {"High": 0, "Medium": 1, "Low": 2}
    insights["severity_order"] = insights["severity"].map(severity_order).fillna(3)
    result = insights.sort_values(["severity_order", "ticker"]).head(5)

    records = serialize_records(
        result[
            [
                "date",
                "ticker",
                "issuer_name",
                "sector",
                "insight_title",
                "insight_summary",
                "business_interpretation",
                "recommended_question",
                "severity",
            ]
        ]
    )
    answer = "The most relevant market insights are sorted by severity and grounded in the Gold insight dataset."
    return AgentResponse(question, answer, records, ["gold_ai_insights"], SUPPORTED_QUESTIONS)


def answer_unsupported(question: str) -> AgentResponse:
    answer = "I can only answer supported market intelligence questions using the current Gold datasets."
    return AgentResponse(question, answer, [], [], SUPPORTED_QUESTIONS)


def answer_question(question: str) -> dict[str, Any]:
    intent = detect_intent(question)
    handlers = {
        "best_performance": answer_best_performance,
        "controlled_growth": answer_controlled_growth,
        "sector_volatility": answer_sector_volatility,
        "unusual_volume": answer_unusual_volume,
        "market_insights": answer_market_insights,
        "unsupported": answer_unsupported,
    }

    return handlers[intent](question).to_dict()
