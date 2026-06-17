# Data Products

## Product Strategy

The platform treats public market data as the input for reusable data products, not as the final deliverable.

The value chain is:

```text
Raw prices -> Clean signals -> Business metrics -> API products -> AI-ready answers
```

The Gold layer is where market data becomes monetizable. Each Gold dataset is shaped around a business question that a financial analyst, market data customer, issuer relations team, or intelligence product could consume.

## Gold Products

### gold_performance

Purpose:

Identify issuers with positive, negative, or sustained price performance.

Main metrics:

```text
return_7d
return_30d
return_90d
performance_rank_30d
performance_category
```

Business value:

- Rank winners and losers in the Mexican equity universe.
- Build market summary products.
- Feed alerts about recent momentum.
- Support issuer comparison dashboards.

Example questions:

- Which issuers had the best 30-day performance?
- Which issuers underperformed recently?
- Which sectors contain the strongest performers?

### gold_volatility

Purpose:

Measure issuer risk through rolling volatility windows.

Main metrics:

```text
volatility_7d
volatility_30d
volatility_90d
risk_level
```

Business value:

- Classify issuers by risk level.
- Support risk-aware ranking products.
- Identify sectors with elevated uncertainty.
- Combine with performance to find attractive risk-return profiles.

Example questions:

- Which sectors show higher volatility?
- Which issuers have elevated short-term risk?
- Which issuers combine growth with controlled volatility?

### gold_liquidity

Purpose:

Measure trading activity and market participation.

Main metrics:

```text
volume
avg_volume_30d
max_volume_30d
min_volume_30d
volume_variation_pct
liquidity_score
liquidity_rank
```

Business value:

- Identify issuers with high or changing trading activity.
- Detect unusual volume behavior.
- Support liquidity rankings for market data users.
- Help segment issuers by market participation.

Example questions:

- Which companies show unusual volume behavior?
- Which issuers are the most liquid?
- Which issuers have volume above their recent average?

### gold_market_trends

Purpose:

Compare issuer-level trends against sector behavior.

Main metrics:

```text
trend_flag
sector_avg_return_30d
issuer_return_30d
market_participation
trend_strength
```

Business value:

- Explain whether movement is issuer-specific or sector-wide.
- Identify issuers diverging from their sector.
- Support sector intelligence products.
- Provide context for AI-generated market explanations.

Example questions:

- Which issuers are outperforming their sector?
- Which sectors are trending positively?
- Which issuers show strong divergence from sector behavior?

### gold_ai_insights

Purpose:

Prepare concise, explainable, AI-ready insights grounded in computed market signals.

Main fields:

```text
insight_title
insight_summary
business_interpretation
recommended_question
severity
```

Business value:

- Provide ready-to-use narratives for analysts.
- Feed AI Agent responses without inventing facts.
- Support alerting and executive summaries.
- Convert quantitative signals into business language.

Example questions:

- What are the most relevant market insights?
- Which issuers require attention?
- What follow-up question should an analyst ask?

## Monetization Patterns

The Gold datasets can support several data product models:

- API subscriptions for market intelligence endpoints.
- Analyst dashboards for performance, risk, liquidity, and trends.
- Daily market insight reports generated from `gold_ai_insights`.
- Premium alerting based on unusual volume, negative pressure, or high volatility.
- Sector intelligence products for issuer relations, research, or sales teams.

## AI Grounding

The AI Agent uses Gold datasets as its only source of truth.

This design keeps the AI behavior controlled:

- Answers are traceable to named datasets.
- Responses include supporting data points.
- Unsupported questions return suggested questions.
- The system avoids external claims and unsupported predictions.

This is intentionally conservative for the MVP. A future LLM integration could improve language quality, but it should still use Gold datasets as the retrieval and grounding layer.
