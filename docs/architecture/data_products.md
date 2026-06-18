# Data Products

## Product Strategy

The platform treats public market data as the input for reusable data products, not as the final deliverable.

The value chain is:

```text
Data -> Information -> Insights -> Products -> Monetization
```

The Gold layer is where market data becomes monetizable. Each Gold dataset is shaped around a business question that a financial analyst, market data customer, issuer relations team, or intelligence product could consume.

The objective is Market Intelligence, not market prediction. The current products describe, compare, rank, explain, and distribute governed historical signals. They do not produce trading recommendations, investment advice, or price forecasts.

For a stock exchange or market data business, this is the difference between data availability and revenue. Prices and volumes become more valuable when they are governed, compared, ranked, explained, distributed through APIs, and packaged for specific customer workflows.

## Business Audience Mapping

| Audience | Needs | Relevant Products |
| --- | --- | --- |
| Issuers | Understand market perception, liquidity, and sector comparison | `gold_performance`, `gold_liquidity`, `gold_market_trends` |
| Brokers and analysts | Monitor market behavior, compare issuers, and explain movement | `gold_performance`, `gold_volatility`, `gold_ai_insights` |
| Fintechs and data vendors | Integrate reliable enriched market data | All Gold datasets through API |
| Exchange commercial teams | Support premium data services and issuer conversations | Dashboard, reports, metadata catalog |
| Executives | Consume concise, explainable market narratives | `gold_ai_insights`, dashboard summaries |

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
- Feed alerts about observed recent movement.
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
- Combine with performance to describe issuer risk-return context.

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
- Feed Governed AI Agent responses without inventing facts.
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
- Issuer intelligence packages that compare each listed company against sector and market behavior.
- Enterprise tiers with API keys, entitlements, SLAs, and customer-specific reporting.

## Revenue Logic

The platform creates business value through repeatable information products:

| Dataset | Product Logic | Revenue Opportunity |
| --- | --- | --- |
| `gold_performance` | Turns price history into rankings, observed movement, and issuer comparison | Market summary feeds, premium dashboards, analyst subscriptions |
| `gold_volatility` | Turns returns into risk signals | Risk intelligence products, alerts, institutional dashboards |
| `gold_liquidity` | Turns volume into participation and unusual activity signals | Liquidity analytics, issuer relations packages, market activity monitoring tools |
| `gold_market_trends` | Adds sector context and relative behavior | Sector intelligence reports, issuer benchmarking, executive narratives |
| `gold_ai_insights` | Converts computed signals into explainable business language | Governed AI assistant, automated reports, client-ready insight feeds |

## Governed AI Grounding

The deterministic Governed AI Agent and the optional LLM-governed assistant use Gold datasets as their only source of truth.

This design keeps the AI behavior controlled:

- Answers are traceable to named datasets.
- Responses include supporting data points.
- Unsupported questions return suggested questions.
- The system avoids external claims and unsupported predictions.
- The system refuses price forecasts and buy/sell recommendations.

This is intentionally conservative for the MVP. The current LLM assistant uses structured Gold context rather than open-ended external retrieval. A future larger-scale RAG layer could add documents, reports, or licensed content, but Gold datasets should remain the grounding layer.
