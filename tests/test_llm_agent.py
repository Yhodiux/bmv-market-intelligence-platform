from src.ai_agent.llm_agent import answer_question_llm, build_evidence_packet, build_prompt


def test_llm_agent_rejects_out_of_domain_question_without_llm_call() -> None:
    response = answer_question_llm("Who won the World Cup?")

    assert response["guardrail_status"] == "blocked_out_of_domain"
    assert response["llm_enabled"] is False
    assert response["source_datasets"] == []
    assert response["evidence"] == []


def test_llm_agent_rejects_predictive_or_advisory_question_without_llm_call() -> None:
    response = answer_question_llm("Should I buy WALMEX.MX tomorrow?")

    assert response["guardrail_status"] == "blocked_predictive_or_advisory"
    assert response["llm_enabled"] is False
    assert response["source_datasets"] == []
    assert response["evidence"] == []


def test_llm_agent_builds_ticker_evidence_packet() -> None:
    packet = build_evidence_packet("Explain WALMEX.MX in executive terms.")

    assert packet.scope == "ticker"
    assert packet.source_datasets == [
        "gold_performance",
        "gold_volatility",
        "gold_liquidity",
        "gold_market_trends",
    ]
    assert len(packet.evidence) == 1
    assert packet.evidence[0]["ticker"] == "WALMEX.MX"


def test_llm_agent_returns_controlled_configuration_message_without_api_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("ENABLE_LLM_AGENT", "true")

    response = answer_question_llm("Explain WALMEX.MX in executive terms.")

    assert response["guardrail_status"] == "llm_not_configured"
    assert response["llm_enabled"] is False
    assert response["source_datasets"]
    assert response["evidence"]


def test_llm_prompt_includes_governed_context() -> None:
    packet = build_evidence_packet("Show me the latest market snapshot.")
    prompt = build_prompt("Show me the latest market snapshot.", packet)

    assert "Governed context" in prompt
    assert "source_datasets" in prompt
    assert "gold_performance" in prompt


def test_llm_agent_returns_controlled_provider_error(monkeypatch) -> None:
    def raise_provider_error(prompt: str, model: str, api_key: str) -> str:
        raise Exception("provider unavailable")

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("ENABLE_LLM_AGENT", "true")
    monkeypatch.setattr("src.ai_agent.llm_agent.call_openai_llm", raise_provider_error)

    response = answer_question_llm("Explain WALMEX.MX in executive terms.")

    assert response["guardrail_status"] == "llm_provider_error"
    assert response["llm_enabled"] is False
    assert response["source_datasets"]
    assert response["evidence"]
