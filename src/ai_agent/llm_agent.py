from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Any

import pandas as pd

from src.ai_agent.market_agent import (
    SUPPORTED_QUESTIONS,
    extract_tickers,
    is_in_domain,
    is_predictive_or_advisory,
    latest_snapshot,
    read_dataset,
    serialize_records,
)


DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"
MAX_EVIDENCE_RECORDS = 20

SYSTEM_INSTRUCTIONS = """
You are a governed market intelligence assistant for Mexican market data products.
Use only the provided structured context.
Do not use external knowledge.
Do not forecast prices, returns, exchange rates, or market events.
Do not provide buy, sell, hold, portfolio, or investment recommendations.
If the context is insufficient, say that the current Gold datasets do not contain enough evidence.
Keep the answer concise, business-oriented, and grounded in the evidence.
Mention the source datasets used.
""".strip()


@dataclass(frozen=True)
class EvidencePacket:
    question: str
    scope: str
    source_datasets: list[str]
    evidence: list[dict[str, Any]]

    def to_context_text(self) -> str:
        return json.dumps(
            {
                "question": self.question,
                "scope": self.scope,
                "source_datasets": self.source_datasets,
                "evidence": self.evidence,
            },
            ensure_ascii=False,
            default=str,
            indent=2,
        )


@dataclass(frozen=True)
class LlmAgentResponse:
    question: str
    answer: str
    source_datasets: list[str]
    evidence: list[dict[str, Any]]
    llm_enabled: bool
    guardrail_status: str
    model: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "answer": self.answer,
            "source_datasets": self.source_datasets,
            "evidence": self.evidence,
            "llm_enabled": self.llm_enabled,
            "guardrail_status": self.guardrail_status,
            "model": self.model,
            "supported_questions": SUPPORTED_QUESTIONS,
        }


def get_llm_model() -> str:
    return os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)


def is_llm_enabled() -> bool:
    return os.getenv("ENABLE_LLM_AGENT", "true").strip().lower() in {"1", "true", "yes", "on"}


def get_openai_api_key() -> str | None:
    return os.getenv("OPENAI_API_KEY")


def reject_response(question: str, answer: str, guardrail_status: str) -> LlmAgentResponse:
    return LlmAgentResponse(
        question=question,
        answer=answer,
        source_datasets=[],
        evidence=[],
        llm_enabled=False,
        guardrail_status=guardrail_status,
        model=None,
    )


def validate_question(question: str) -> LlmAgentResponse | None:
    if is_predictive_or_advisory(question):
        return reject_response(
            question,
            (
                "I cannot provide forecasts, price targets, or buy/sell recommendations. "
                "I can answer descriptive market intelligence questions grounded in the current Gold datasets."
            ),
            "blocked_predictive_or_advisory",
        )

    if not is_in_domain(question):
        return reject_response(
            question,
            "I can only answer governed market intelligence questions grounded in the current Gold datasets.",
            "blocked_out_of_domain",
        )

    return None


def normalize_text(value: str) -> str:
    return value.strip().lower()


def available_sectors() -> set[str]:
    performance = read_dataset("gold_performance")
    return {str(sector) for sector in performance["sector"].dropna().unique()}


def extract_sectors(question: str) -> list[str]:
    normalized = normalize_text(question)
    sectors = []
    for sector in sorted(available_sectors(), key=len, reverse=True):
        if normalize_text(sector) in normalized:
            sectors.append(sector)
    return sectors


def latest_joined_market_data() -> pd.DataFrame:
    performance = latest_snapshot(read_dataset("gold_performance"))
    volatility = latest_snapshot(read_dataset("gold_volatility"))
    liquidity = latest_snapshot(read_dataset("gold_liquidity"))
    trends = latest_snapshot(read_dataset("gold_market_trends"))

    return (
        performance.merge(
            volatility[["ticker", "date", "volatility_30d", "volatility_90d", "risk_level"]],
            on=["ticker", "date"],
            how="left",
            validate="one_to_one",
        )
        .merge(
            liquidity[
                [
                    "ticker",
                    "date",
                    "volume",
                    "avg_volume_30d",
                    "volume_variation_pct",
                    "liquidity_score",
                    "liquidity_rank",
                ]
            ],
            on=["ticker", "date"],
            how="left",
            validate="one_to_one",
        )
        .merge(
            trends[
                [
                    "ticker",
                    "date",
                    "trend_flag",
                    "sector_avg_return_30d",
                    "market_participation",
                    "trend_strength",
                ]
            ],
            on=["ticker", "date"],
            how="left",
            validate="one_to_one",
        )
    )


def build_ticker_evidence(question: str, tickers: list[str]) -> EvidencePacket:
    latest = latest_joined_market_data()
    selected = latest.loc[latest["ticker"].astype(str).str.upper().isin(tickers)].copy()
    selected = selected.sort_values("return_30d", ascending=False).head(MAX_EVIDENCE_RECORDS)

    return EvidencePacket(
        question=question,
        scope="ticker",
        source_datasets=[
            "gold_performance",
            "gold_volatility",
            "gold_liquidity",
            "gold_market_trends",
        ],
        evidence=serialize_records(selected),
    )


def build_sector_evidence(question: str, sectors: list[str]) -> EvidencePacket:
    latest = latest_joined_market_data()
    selected = latest.loc[latest["sector"].astype(str).isin(sectors)].copy()
    sector_summary = (
        selected.groupby("sector", as_index=False)
        .agg(
            issuer_count=("ticker", "nunique"),
            avg_return_30d=("return_30d", "mean"),
            best_return_30d=("return_30d", "max"),
            avg_volatility_30d=("volatility_30d", "mean"),
            high_risk_issuers=("risk_level", lambda values: int((values == "High").sum())),
            avg_liquidity_score=("liquidity_score", "mean"),
        )
        .sort_values("avg_return_30d", ascending=False)
    )

    return EvidencePacket(
        question=question,
        scope="sector",
        source_datasets=[
            "gold_performance",
            "gold_volatility",
            "gold_liquidity",
            "gold_market_trends",
        ],
        evidence=serialize_records(sector_summary.head(MAX_EVIDENCE_RECORDS)),
    )


def build_market_evidence(question: str) -> EvidencePacket:
    latest = latest_joined_market_data()
    insights = read_dataset("gold_ai_insights")
    severity_order = {"High": 0, "Medium": 1, "Low": 2}
    ranked_insights = insights.copy()
    ranked_insights["severity_order"] = ranked_insights["severity"].map(severity_order).fillna(3)

    market_summary = {
        "date": latest["date"].max(),
        "issuer_count": int(latest["ticker"].nunique()),
        "avg_return_30d": latest["return_30d"].mean(),
        "positive_30d_issuers": int((latest["return_30d"] > 0).sum()),
        "negative_30d_issuers": int((latest["return_30d"] < 0).sum()),
        "high_risk_issuers": int((latest["risk_level"] == "High").sum()),
        "avg_liquidity_score": latest["liquidity_score"].mean(),
    }

    top_performers = latest.sort_values("return_30d", ascending=False).head(5)
    weakest_performers = latest.sort_values("return_30d", ascending=True).head(5)
    most_liquid = latest.sort_values("liquidity_score", ascending=False).head(5)
    highest_risk = latest.sort_values("volatility_30d", ascending=False).head(5)
    top_insights = ranked_insights.sort_values(["severity_order", "ticker"]).head(5)

    evidence = [
        {"section": "market_summary", **serialize_records(pd.DataFrame([market_summary]))[0]},
        {"section": "top_performers", "records": serialize_records(top_performers)},
        {"section": "weakest_performers", "records": serialize_records(weakest_performers)},
        {"section": "most_liquid", "records": serialize_records(most_liquid)},
        {"section": "highest_volatility", "records": serialize_records(highest_risk)},
        {"section": "top_insights", "records": serialize_records(top_insights)},
    ]

    return EvidencePacket(
        question=question,
        scope="market",
        source_datasets=[
            "gold_performance",
            "gold_volatility",
            "gold_liquidity",
            "gold_market_trends",
            "gold_ai_insights",
        ],
        evidence=evidence,
    )


def build_evidence_packet(question: str) -> EvidencePacket:
    tickers = extract_tickers(question)
    if tickers:
        return build_ticker_evidence(question, tickers)

    sectors = extract_sectors(question)
    if sectors:
        return build_sector_evidence(question, sectors)

    return build_market_evidence(question)


def build_prompt(question: str, evidence_packet: EvidencePacket) -> str:
    return (
        "Answer the user question using only this governed structured context.\n\n"
        f"User question:\n{question}\n\n"
        f"Governed context:\n{evidence_packet.to_context_text()}"
    )


def call_openai_llm(prompt: str, model: str, api_key: str) -> str:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("The openai package is not installed.") from exc

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=model,
        instructions=SYSTEM_INSTRUCTIONS,
        input=prompt,
        max_output_tokens=500,
    )
    return response.output_text.strip()


def answer_question_llm(question: str) -> dict[str, Any]:
    guardrail_response = validate_question(question)
    if guardrail_response is not None:
        return guardrail_response.to_dict()

    evidence_packet = build_evidence_packet(question)
    if not evidence_packet.evidence:
        return reject_response(
            question,
            "The current Gold datasets do not contain enough evidence to answer that question.",
            "insufficient_context",
        ).to_dict()

    if not is_llm_enabled():
        return reject_response(
            question,
            "The LLM-governed agent is disabled. Set ENABLE_LLM_AGENT=true to enable it.",
            "llm_disabled",
        ).to_dict()

    api_key = get_openai_api_key()
    model = get_llm_model()
    if not api_key:
        return LlmAgentResponse(
            question=question,
            answer="The LLM-governed agent is not configured. Set OPENAI_API_KEY to enable model-backed answers.",
            source_datasets=evidence_packet.source_datasets,
            evidence=evidence_packet.evidence,
            llm_enabled=False,
            guardrail_status="llm_not_configured",
            model=model,
        ).to_dict()

    prompt = build_prompt(question, evidence_packet)
    try:
        answer = call_openai_llm(prompt, model, api_key)
    except RuntimeError:
        raise
    except Exception as exc:
        return LlmAgentResponse(
            question=question,
            answer=(
                f"The LLM provider returned an error: {type(exc).__name__}. "
                "The governed Gold evidence is still available for review."
            ),
            source_datasets=evidence_packet.source_datasets,
            evidence=evidence_packet.evidence,
            llm_enabled=False,
            guardrail_status="llm_provider_error",
            model=model,
        ).to_dict()

    return LlmAgentResponse(
        question=question,
        answer=answer,
        source_datasets=evidence_packet.source_datasets,
        evidence=evidence_packet.evidence,
        llm_enabled=True,
        guardrail_status="allowed",
        model=model,
    ).to_dict()
