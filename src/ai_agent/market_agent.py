from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import re

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
    "Which issuers had the weakest 30-day performance?",
    "Which issuers have the highest liquidity?",
    "Which issuers have high risk levels?",
    "Which sectors had the strongest 30-day performance?",
    "Show me the latest market snapshot.",
    "Summarize WALMEX.MX.",
    "Compare WALMEX.MX and CEMEXCPO.MX.",
]

DOMAIN_TERMS = [
    "issuer",
    "issuers",
    "company",
    "companies",
    "ticker",
    "sector",
    "market",
    "performance",
    "return",
    "volatility",
    "risk",
    "volume",
    "liquidity",
    "trend",
    "insight",
    "dataset",
    "gold",
    "emisor",
    "emisora",
    "emisoras",
    "empresa",
    "empresas",
    "mercado",
    "rendimiento",
    "retorno",
    "volatilidad",
    "riesgo",
    "volumen",
    "liquidez",
    "tendencia",
    "datos",
]

OUT_OF_DOMAIN_TERMS = [
    "weather",
    "climate",
    "world cup",
    "football",
    "soccer",
    "sports",
    "movie",
    "music",
    "president",
    "election",
    "guerra",
    "mundial",
    "copa del mundo",
    "futbol",
    "deporte",
    "clima",
    "pelicula",
    "musica",
    "presidente",
    "eleccion",
]

PREDICTIVE_TERMS = [
    "predict",
    "forecast",
    "tomorrow",
    "next week",
    "next month",
    "buy",
    "sell",
    "recommend",
    "price target",
    "predecir",
    "pronosticar",
    "manana",
    "mañana",
    "proxima semana",
    "próxima semana",
    "comprar",
    "vender",
    "recomiendas",
    "precio objetivo",
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


def get_known_tickers() -> set[str]:
    performance = read_dataset("gold_performance")
    tickers = performance["ticker"].astype(str).str.upper()
    return set(tickers)


def extract_tickers(question: str) -> list[str]:
    known_tickers = get_known_tickers()
    normalized = question.upper().replace("_", ".")
    found: list[str] = []

    for ticker in sorted(known_tickers, key=len, reverse=True):
        ticker_aliases = {ticker, ticker.replace(".", "_"), ticker.replace(".MX", "")}
        for alias in ticker_aliases:
            pattern = rf"(?<![A-Z0-9]){re.escape(alias)}(?![A-Z0-9])"
            if re.search(pattern, normalized) and ticker not in found:
                found.append(ticker)

    return found


def is_predictive_or_advisory(question: str) -> bool:
    normalized = question.lower()
    return any(term in normalized for term in PREDICTIVE_TERMS)


def is_in_domain(question: str) -> bool:
    normalized = question.lower()
    if any(term in normalized for term in OUT_OF_DOMAIN_TERMS):
        return False
    if any(term in normalized for term in DOMAIN_TERMS):
        return True
    return bool(extract_tickers(question))


def detect_intent(question: str) -> str:
    normalized = question.lower()
    tickers = extract_tickers(question)

    if len(tickers) >= 2 or any(term in normalized for term in ["compare", "versus", "vs", "comparar", "compara"]):
        return "compare_issuers"

    if len(tickers) == 1 or any(term in normalized for term in ["summarize", "summary", "resume", "resumen"]):
        return "issuer_summary"

    if any(term in normalized for term in ["weakest", "worst", "bottom", "underperform", "peor", "peores", "bajo rendimiento"]):
        return "weakest_performance"

    if any(term in normalized for term in ["highest liquidity", "most liquid", "mayor liquidez", "mas liquidez", "más liquidez"]):
        return "highest_liquidity"

    if any(term in normalized for term in ["high risk", "highest risk", "alto riesgo", "mayor riesgo"]):
        return "high_risk"

    if any(term in normalized for term in ["sector"]):
        if any(term in normalized for term in ["best", "strongest", "performance", "return", "mejor", "rendimiento"]):
            return "sector_performance"
        return "sector_volatility"

    if any(term in normalized for term in ["snapshot", "overview", "general", "market status", "estado del mercado"]):
        return "market_snapshot"

    if any(term in normalized for term in ["best", "top", "performance", "rendimiento", "mejor"]):
        return "best_performance"

    if any(term in normalized for term in ["sustained", "growth", "controlled", "crecimiento", "controlada"]):
        return "controlled_growth"

    if any(term in normalized for term in ["volatility", "volatilidad", "risk", "riesgo"]):
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


def answer_weakest_performance(question: str) -> AgentResponse:
    performance = latest_snapshot(read_dataset("gold_performance"))
    result = (
        performance.dropna(subset=["return_30d"])
        .sort_values(["return_30d", "performance_rank_30d"], ascending=[True, False])
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
    answer = "The weakest 30-day performers are ranked using the latest Gold performance snapshot."
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


def answer_highest_liquidity(question: str) -> AgentResponse:
    liquidity = latest_snapshot(read_dataset("gold_liquidity"))
    result = liquidity.sort_values(["liquidity_score", "avg_volume_30d"], ascending=[False, False]).head(5)

    records = serialize_records(
        result[
            [
                "date",
                "ticker",
                "issuer_name",
                "sector",
                "volume",
                "avg_volume_30d",
                "liquidity_score",
                "liquidity_rank",
            ]
        ]
    )
    answer = "The highest-liquidity issuers are ranked by liquidity score in the latest Gold liquidity snapshot."
    return AgentResponse(question, answer, records, ["gold_liquidity"], SUPPORTED_QUESTIONS)


def answer_high_risk(question: str) -> AgentResponse:
    volatility = latest_snapshot(read_dataset("gold_volatility"))
    risk_order = {"High": 0, "Medium": 1, "Low": 2, "Unknown": 3}
    result = volatility.copy()
    result["risk_order"] = result["risk_level"].map(risk_order).fillna(4)
    result = result.sort_values(["risk_order", "volatility_30d"], ascending=[True, False]).head(5)

    records = serialize_records(
        result[
            [
                "date",
                "ticker",
                "issuer_name",
                "sector",
                "volatility_30d",
                "volatility_90d",
                "risk_level",
            ]
        ]
    )
    answer = "High-risk issuers are identified from 30-day volatility and the Gold risk classification."
    return AgentResponse(question, answer, records, ["gold_volatility"], SUPPORTED_QUESTIONS)


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


def answer_sector_performance(question: str) -> AgentResponse:
    performance = latest_snapshot(read_dataset("gold_performance"))
    sector_performance = (
        performance.dropna(subset=["return_30d"])
        .groupby("sector", as_index=False)
        .agg(
            avg_return_30d=("return_30d", "mean"),
            max_return_30d=("return_30d", "max"),
            issuer_count=("ticker", "nunique"),
        )
        .sort_values("avg_return_30d", ascending=False)
    )

    records = serialize_records(sector_performance.head(5))
    answer = "Sectors with stronger performance are ranked by average 30-day return in the latest snapshot."
    return AgentResponse(question, answer, records, ["gold_performance"], SUPPORTED_QUESTIONS)


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


def answer_market_snapshot(question: str) -> AgentResponse:
    performance = latest_snapshot(read_dataset("gold_performance"))
    volatility = latest_snapshot(read_dataset("gold_volatility"))
    liquidity = latest_snapshot(read_dataset("gold_liquidity"))

    latest_date = performance["date"].max()
    record = {
        "date": latest_date,
        "issuer_count": int(performance["ticker"].nunique()),
        "avg_return_30d": performance["return_30d"].mean(),
        "positive_30d_issuers": int((performance["return_30d"] > 0).sum()),
        "negative_30d_issuers": int((performance["return_30d"] < 0).sum()),
        "high_risk_issuers": int((volatility["risk_level"] == "High").sum()),
        "avg_liquidity_score": liquidity["liquidity_score"].mean(),
    }

    records = serialize_records(pd.DataFrame([record]))
    answer = "The latest market snapshot summarizes issuer coverage, 30-day returns, risk, and liquidity."
    return AgentResponse(
        question,
        answer,
        records,
        ["gold_performance", "gold_volatility", "gold_liquidity"],
        SUPPORTED_QUESTIONS,
    )


def answer_issuer_summary(question: str) -> AgentResponse:
    tickers = extract_tickers(question)
    if not tickers:
        return answer_unsupported(question)

    ticker = tickers[0]
    performance = latest_snapshot(read_dataset("gold_performance"))
    volatility = latest_snapshot(read_dataset("gold_volatility"))
    liquidity = latest_snapshot(read_dataset("gold_liquidity"))

    summary = (
        performance.loc[performance["ticker"].astype(str).str.upper() == ticker]
        .merge(
            volatility[["ticker", "date", "volatility_30d", "risk_level"]],
            on=["ticker", "date"],
            how="left",
            validate="one_to_one",
        )
        .merge(
            liquidity[["ticker", "date", "volume", "avg_volume_30d", "liquidity_score", "liquidity_rank"]],
            on=["ticker", "date"],
            how="left",
            validate="one_to_one",
        )
    )

    if summary.empty:
        return answer_unsupported(question)

    records = serialize_records(
        summary[
            [
                "date",
                "ticker",
                "issuer_name",
                "sector",
                "return_7d",
                "return_30d",
                "return_90d",
                "performance_category",
                "volatility_30d",
                "risk_level",
                "volume",
                "avg_volume_30d",
                "liquidity_score",
                "liquidity_rank",
            ]
        ]
    )
    answer = f"{ticker} is summarized from the latest Gold performance, volatility, and liquidity snapshots."
    return AgentResponse(
        question,
        answer,
        records,
        ["gold_performance", "gold_volatility", "gold_liquidity"],
        SUPPORTED_QUESTIONS,
    )


def answer_compare_issuers(question: str) -> AgentResponse:
    tickers = extract_tickers(question)
    if len(tickers) < 2:
        return answer_unsupported(question)

    requested = tickers[:2]
    performance = latest_snapshot(read_dataset("gold_performance"))
    volatility = latest_snapshot(read_dataset("gold_volatility"))
    liquidity = latest_snapshot(read_dataset("gold_liquidity"))

    comparison = (
        performance.loc[performance["ticker"].astype(str).str.upper().isin(requested)]
        .merge(
            volatility[["ticker", "date", "volatility_30d", "risk_level"]],
            on=["ticker", "date"],
            how="left",
            validate="one_to_one",
        )
        .merge(
            liquidity[["ticker", "date", "liquidity_score", "liquidity_rank"]],
            on=["ticker", "date"],
            how="left",
            validate="one_to_one",
        )
        .sort_values("return_30d", ascending=False)
    )

    if len(comparison) < 2:
        return answer_unsupported(question)

    records = serialize_records(
        comparison[
            [
                "date",
                "ticker",
                "issuer_name",
                "sector",
                "return_30d",
                "return_90d",
                "performance_rank_30d",
                "volatility_30d",
                "risk_level",
                "liquidity_score",
                "liquidity_rank",
            ]
        ]
    )
    answer = "The issuer comparison uses the latest Gold performance, volatility, and liquidity snapshots."
    return AgentResponse(
        question,
        answer,
        records,
        ["gold_performance", "gold_volatility", "gold_liquidity"],
        SUPPORTED_QUESTIONS,
    )


def answer_unsupported(question: str) -> AgentResponse:
    answer = "I can only answer supported market intelligence questions using the current Gold datasets."
    return AgentResponse(question, answer, [], [], SUPPORTED_QUESTIONS)


def answer_out_of_domain(question: str) -> AgentResponse:
    answer = "I can only answer governed market intelligence questions grounded in the current Gold datasets."
    return AgentResponse(question, answer, [], [], SUPPORTED_QUESTIONS)


def answer_predictive_or_advisory(question: str) -> AgentResponse:
    answer = (
        "I cannot provide forecasts, price targets, or buy/sell recommendations. "
        "I can answer descriptive market intelligence questions grounded in the current Gold datasets."
    )
    return AgentResponse(question, answer, [], [], SUPPORTED_QUESTIONS)


def answer_question(question: str) -> dict[str, Any]:
    if is_predictive_or_advisory(question):
        return answer_predictive_or_advisory(question).to_dict()

    if not is_in_domain(question):
        return answer_out_of_domain(question).to_dict()

    intent = detect_intent(question)
    handlers = {
        "best_performance": answer_best_performance,
        "weakest_performance": answer_weakest_performance,
        "controlled_growth": answer_controlled_growth,
        "highest_liquidity": answer_highest_liquidity,
        "high_risk": answer_high_risk,
        "sector_volatility": answer_sector_volatility,
        "sector_performance": answer_sector_performance,
        "unusual_volume": answer_unusual_volume,
        "market_insights": answer_market_insights,
        "market_snapshot": answer_market_snapshot,
        "issuer_summary": answer_issuer_summary,
        "compare_issuers": answer_compare_issuers,
        "unsupported": answer_unsupported,
    }

    return handlers[intent](question).to_dict()
