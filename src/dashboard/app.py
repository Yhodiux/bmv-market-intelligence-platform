from __future__ import annotations

from pathlib import Path
import sys

import altair as alt
import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ai_agent.llm_agent import answer_question_llm
from src.ai_agent.market_agent import SUPPORTED_QUESTIONS, answer_question

DATA_DIR = PROJECT_ROOT / "data"

GOLD_DATASETS = {
    "Performance": DATA_DIR / "gold" / "gold_performance.parquet",
    "Volatility": DATA_DIR / "gold" / "gold_volatility.parquet",
    "Liquidity": DATA_DIR / "gold" / "gold_liquidity.parquet",
    "Market Trends": DATA_DIR / "gold" / "gold_market_trends.parquet",
    "AI Insights": DATA_DIR / "gold" / "gold_ai_insights.parquet",
}


@st.cache_data
def read_dataset(path: str) -> pd.DataFrame:
    return pd.read_parquet(path)


def load_gold_datasets() -> dict[str, pd.DataFrame]:
    datasets: dict[str, pd.DataFrame] = {}
    for name, path in GOLD_DATASETS.items():
        if path.exists():
            datasets[name] = read_dataset(str(path))
    return datasets


def build_status_table(datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for name, path in GOLD_DATASETS.items():
        data = datasets.get(name)
        rows.append(
            {
                "dataset": name,
                "status": "available" if data is not None else "missing",
                "records": 0 if data is None else len(data),
                "columns": 0 if data is None else len(data.columns),
                "path": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            }
        )
    return pd.DataFrame(rows)


def latest_snapshot(data: pd.DataFrame) -> pd.DataFrame:
    if "date" not in data.columns:
        return data.copy()

    dated = data.copy()
    dated["date"] = pd.to_datetime(dated["date"])
    latest_date = dated["date"].max()
    return dated.loc[dated["date"] == latest_date].copy()


def format_percent_columns(data: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    formatted = data.copy()
    for column in columns:
        if column in formatted.columns:
            formatted[column] = formatted[column].map(lambda value: None if pd.isna(value) else f"{value:.2%}")
    return formatted


def build_return_chart(data: pd.DataFrame, title: str, color: str, sort_descending: bool) -> alt.Chart:
    chart_data = data.copy()
    chart_data["return_30d_pct"] = chart_data["return_30d"] * 100
    chart_data["label"] = chart_data["ticker"].astype(str)

    return (
        alt.Chart(chart_data, title=title)
        .mark_bar(color=color)
        .encode(
            x=alt.X("return_30d_pct:Q", title="30-day return (%)"),
            y=alt.Y("label:N", sort="-x" if sort_descending else "x", title=None),
            tooltip=[
                alt.Tooltip("ticker:N", title="Ticker"),
                alt.Tooltip("issuer_name:N", title="Issuer"),
                alt.Tooltip("sector:N", title="Sector"),
                alt.Tooltip("return_30d_pct:Q", title="30-day return (%)", format=".2f"),
            ],
        )
        .properties(height=260)
    )


def build_sector_volatility_chart(data: pd.DataFrame) -> alt.Chart:
    chart_data = data.copy()
    chart_data["avg_volatility_30d_pct"] = chart_data["avg_volatility_30d"] * 100

    return (
        alt.Chart(chart_data, title="Average 30-day volatility by sector")
        .mark_bar(color="#2563eb")
        .encode(
            x=alt.X("avg_volatility_30d_pct:Q", title="Average 30-day volatility (%)"),
            y=alt.Y("sector:N", sort="-x", title=None),
            tooltip=[
                alt.Tooltip("sector:N", title="Sector"),
                alt.Tooltip("avg_volatility_30d_pct:Q", title="Avg volatility (%)", format=".2f"),
                alt.Tooltip("issuer_count:Q", title="Issuers"),
            ],
        )
        .properties(height=300)
    )


def build_risk_level_chart(data: pd.DataFrame) -> alt.Chart:
    risk_order = ["Low", "Medium", "High", "Unknown"]
    chart_data = data.copy()

    return (
        alt.Chart(chart_data, title="Issuers by risk level")
        .mark_bar(color="#64748b")
        .encode(
            x=alt.X("risk_level:N", sort=risk_order, title="Risk level"),
            y=alt.Y("issuer_count:Q", title="Issuers"),
            tooltip=[
                alt.Tooltip("risk_level:N", title="Risk level"),
                alt.Tooltip("issuer_count:Q", title="Issuers"),
            ],
        )
        .properties(height=300)
    )


def build_volume_variation_chart(data: pd.DataFrame) -> alt.Chart:
    chart_data = data.copy()
    chart_data["volume_variation_pct_display"] = chart_data["volume_variation_pct"] * 100
    chart_data["absolute_volume_variation_pct_display"] = chart_data["absolute_volume_variation_pct"] * 100

    return (
        alt.Chart(chart_data, title="Largest volume variations vs 30-day average")
        .mark_bar(color="#7c3aed")
        .encode(
            x=alt.X("volume_variation_pct_display:Q", title="Volume variation (%)"),
            y=alt.Y(
                "ticker:N",
                sort=alt.EncodingSortField(field="absolute_volume_variation_pct_display", order="descending"),
                title=None,
            ),
            tooltip=[
                alt.Tooltip("ticker:N", title="Ticker"),
                alt.Tooltip("issuer_name:N", title="Issuer"),
                alt.Tooltip("sector:N", title="Sector"),
                alt.Tooltip("volume_variation_pct_display:Q", title="Variation (%)", format=".2f"),
                alt.Tooltip("liquidity_score:Q", title="Liquidity score", format=".2f"),
            ],
        )
        .properties(height=300)
    )


def render_executive_kpis(datasets: dict[str, pd.DataFrame], status: pd.DataFrame) -> None:
    performance = datasets.get("Performance")
    insights = datasets.get("AI Insights")

    latest_date = "n/a"
    issuer_count = 0
    if performance is not None and not performance.empty:
        snapshot = latest_snapshot(performance)
        latest_date = pd.to_datetime(snapshot["date"].max()).strftime("%Y-%m-%d")
        issuer_count = int(snapshot["ticker"].nunique())

    insight_count = 0 if insights is None else len(insights)
    total_records = int(status["records"].sum())

    st.subheader("Executive Overview")
    kpi_date, kpi_issuers, kpi_records, kpi_insights = st.columns(4)
    kpi_date.metric("Latest date", latest_date)
    kpi_issuers.metric("Issuers", issuer_count)
    kpi_records.metric("Gold records", f"{total_records:,}")
    kpi_insights.metric("AI insights", insight_count)


def render_performance_rankings(datasets: dict[str, pd.DataFrame]) -> None:
    performance = datasets.get("Performance")
    if performance is None or performance.empty:
        st.info("Performance dataset is not available.")
        return

    snapshot = latest_snapshot(performance)
    ranking_columns = [
        "ticker",
        "issuer_name",
        "sector",
        "return_7d",
        "return_30d",
        "return_90d",
        "performance_rank_30d",
        "performance_category",
    ]

    top_performers = snapshot.sort_values("return_30d", ascending=False).head(5)[ranking_columns]
    bottom_performers = snapshot.sort_values("return_30d", ascending=True).head(5)[ranking_columns]

    st.subheader("30-Day Performance")
    top_column, bottom_column = st.columns(2)

    with top_column:
        st.markdown("**Top performers**")
        st.altair_chart(
            build_return_chart(top_performers, "Top 5 by 30-day return", "#1f9d55", sort_descending=True),
            use_container_width=True,
        )
        st.dataframe(
            format_percent_columns(top_performers, ["return_7d", "return_30d", "return_90d"]),
            use_container_width=True,
            hide_index=True,
        )

    with bottom_column:
        st.markdown("**Lowest performers**")
        st.altair_chart(
            build_return_chart(bottom_performers, "Bottom 5 by 30-day return", "#c2410c", sort_descending=False),
            use_container_width=True,
        )
        st.dataframe(
            format_percent_columns(bottom_performers, ["return_7d", "return_30d", "return_90d"]),
            use_container_width=True,
            hide_index=True,
        )


def render_risk_section(datasets: dict[str, pd.DataFrame]) -> None:
    volatility = datasets.get("Volatility")
    if volatility is None or volatility.empty:
        st.info("Volatility dataset is not available.")
        return

    snapshot = latest_snapshot(volatility)
    sector_volatility = (
        snapshot.dropna(subset=["volatility_30d"])
        .groupby("sector", as_index=False)
        .agg(
            avg_volatility_30d=("volatility_30d", "mean"),
            max_volatility_30d=("volatility_30d", "max"),
            issuer_count=("ticker", "nunique"),
        )
        .sort_values("avg_volatility_30d", ascending=False)
    )
    risk_counts = (
        snapshot.groupby("risk_level", as_index=False)
        .agg(issuer_count=("ticker", "nunique"))
        .sort_values("issuer_count", ascending=False)
    )

    st.subheader("Risk and Volatility")
    volatility_column, risk_column = st.columns(2, gap="large")

    with volatility_column:
        st.altair_chart(build_sector_volatility_chart(sector_volatility), use_container_width=True)
        st.dataframe(
            format_percent_columns(sector_volatility, ["avg_volatility_30d", "max_volatility_30d"]),
            use_container_width=True,
            hide_index=True,
        )

    with risk_column:
        st.altair_chart(build_risk_level_chart(risk_counts), use_container_width=True)
        st.dataframe(risk_counts, use_container_width=True, hide_index=True)


def render_liquidity_section(datasets: dict[str, pd.DataFrame]) -> None:
    liquidity = datasets.get("Liquidity")
    if liquidity is None or liquidity.empty:
        st.info("Liquidity dataset is not available.")
        return

    snapshot = latest_snapshot(liquidity)
    snapshot["absolute_volume_variation_pct"] = snapshot["volume_variation_pct"].abs()

    unusual_volume = snapshot.sort_values("absolute_volume_variation_pct", ascending=False).head(7)
    top_liquidity = snapshot.sort_values("liquidity_score", ascending=False).head(7)

    liquidity_columns = [
        "ticker",
        "issuer_name",
        "sector",
        "volume",
        "avg_volume_30d",
        "volume_variation_pct",
        "liquidity_score",
        "liquidity_rank",
    ]

    st.subheader("Liquidity and Unusual Volume")
    volume_column, liquidity_column = st.columns(2, gap="large")

    with volume_column:
        st.altair_chart(build_volume_variation_chart(unusual_volume), use_container_width=True)
        st.dataframe(
            format_percent_columns(unusual_volume[liquidity_columns], ["volume_variation_pct"]),
            use_container_width=True,
            hide_index=True,
        )

    with liquidity_column:
        st.markdown("**Top liquidity score**")
        st.dataframe(
            format_percent_columns(top_liquidity[liquidity_columns], ["volume_variation_pct"]),
            use_container_width=True,
            hide_index=True,
        )


def render_ai_insights_section(datasets: dict[str, pd.DataFrame]) -> None:
    insights = datasets.get("AI Insights")
    if insights is None or insights.empty:
        st.info("AI Insights dataset is not available.")
        return

    severity_order = {"High": 0, "Medium": 1, "Low": 2}
    ranked_insights = insights.copy()
    ranked_insights["severity_order"] = ranked_insights["severity"].map(severity_order).fillna(3)
    ranked_insights = ranked_insights.sort_values(["severity_order", "ticker"]).head(6)

    st.subheader("AI-Ready Insights")
    insight_columns = st.columns(3)

    for index, row in enumerate(ranked_insights.to_dict(orient="records")):
        with insight_columns[index % 3]:
            st.markdown(f"**{row['severity']} | {row['ticker']}**")
            st.markdown(row["insight_title"])
            st.caption(row["insight_summary"])
            st.write(row["business_interpretation"])
            st.caption(f"Recommended question: {row['recommended_question']}")


def render_ai_agent_section() -> None:
    with st.container(border=True):
        st.subheader("Ask the Market Intelligence Agent")
        st.caption("Explore trusted market intelligence through governed questions backed by Gold datasets.")

        selected_question = st.selectbox("Suggested question", SUPPORTED_QUESTIONS)
        question = st.text_input("Question", value=selected_question)
        response = answer_question(question)

        st.markdown("**Answer**")
        st.write(response["answer"])

        source_datasets = ", ".join(response["source_datasets"]) if response["source_datasets"] else "n/a"
        st.caption(f"Source datasets: {source_datasets}")

        data_points = pd.DataFrame(response["data_points"])
        if not data_points.empty:
            st.dataframe(data_points, use_container_width=True, hide_index=True)
        else:
            st.info("No data points returned for this question.")


def render_llm_agent_section() -> None:
    with st.container(border=True):
        st.subheader("LLM-Governed Market Assistant")
        st.caption("Ask open questions while keeping every response constrained to governed market evidence.")

        question = st.text_area(
            "Open market intelligence question",
            value="Explain WALMEX.MX in executive terms.",
            height=90,
        )

        if not question.strip():
            st.info("Enter a market intelligence question grounded in the Gold datasets.")
            return

        response = answer_question_llm(question)

        st.markdown("**Answer**")
        st.write(response["answer"])

        status_columns = st.columns(3)
        status_columns[0].metric("Guardrail status", response["guardrail_status"])
        status_columns[1].metric("LLM enabled", "yes" if response["llm_enabled"] else "no")
        status_columns[2].metric("Model", response["model"] or "n/a")

        source_datasets = ", ".join(response["source_datasets"]) if response["source_datasets"] else "n/a"
        st.caption(f"Source datasets: {source_datasets}")

        evidence = response["evidence"]
        if evidence:
            with st.expander("Evidence used", expanded=False):
                st.json(evidence)
        else:
            st.info("No evidence was used because the request did not pass guardrails or context was unavailable.")


def main() -> None:
    st.set_page_config(
        page_title="Mexico Equity Intelligence",
        page_icon="chart_with_upwards_trend",
        layout="wide",
    )

    st.title("Mexico Equity Intelligence Platform")
    st.caption("Local dashboard for Gold data products and AI-ready market intelligence.")

    datasets = load_gold_datasets()
    status = build_status_table(datasets)

    available_count = int((status["status"] == "available").sum())
    total_records = int(status["records"].sum())

    metric_left, metric_middle, metric_right = st.columns(3)
    metric_left.metric("Gold datasets", f"{available_count}/{len(GOLD_DATASETS)}")
    metric_middle.metric("Total records", f"{total_records:,}")
    metric_right.metric("Missing datasets", int((status["status"] == "missing").sum()))

    st.subheader("Dataset Status")
    st.dataframe(status, use_container_width=True, hide_index=True)

    if not datasets:
        st.warning("Run `docker compose run --rm pipeline` before opening the dashboard.")
        return

    render_executive_kpis(datasets, status)
    render_performance_rankings(datasets)
    st.divider()
    render_risk_section(datasets)
    st.divider()
    render_liquidity_section(datasets)
    st.divider()
    render_ai_insights_section(datasets)

    st.divider()
    st.header("Governed Market Intelligence")
    st.caption("Turn trusted Gold data products into auditable answers and executive explanations.")
    render_ai_agent_section()
    render_llm_agent_section()

    st.divider()
    selected_dataset = st.selectbox("Preview dataset", list(datasets.keys()))
    preview = datasets[selected_dataset].head(20)

    st.subheader(f"{selected_dataset} Preview")
    st.dataframe(preview, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
