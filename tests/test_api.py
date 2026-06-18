from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_gold_dataset_endpoints_return_records() -> None:
    for endpoint in ["/performance", "/volatility", "/liquidity", "/market-trends", "/ai-insights"]:
        response = client.get(endpoint, params={"limit": 1})

        assert response.status_code == 200
        assert len(response.json()) == 1


def test_datasets_endpoint_returns_metadata_catalog() -> None:
    response = client.get("/datasets")
    payload = response.json()

    assert response.status_code == 200
    assert payload["dataset_count"] == 7


def test_questions_endpoint_returns_supported_questions() -> None:
    response = client.get("/questions")
    payload = response.json()

    assert response.status_code == 200
    assert payload["question_count"] == len(payload["supported_questions"])
    assert payload["question_count"] == 12
    assert "guardrail" in payload


def test_ask_endpoint_answers_supported_question() -> None:
    response = client.post(
        "/ask",
        json={"question": "Which issuers had the best 30-day performance?"},
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["source_datasets"] == ["gold_performance"]
    assert len(payload["data_points"]) > 0


def test_ask_endpoint_returns_suggestions_for_unsupported_question() -> None:
    response = client.post(
        "/ask",
        json={"question": "What is the weather today?"},
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["data_points"] == []
    assert payload["source_datasets"] == []
    assert len(payload["supported_questions"]) == 12


def test_ask_llm_endpoint_returns_controlled_configuration_message_without_api_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("ENABLE_LLM_AGENT", "true")

    response = client.post(
        "/ask-llm",
        json={"question": "Explain WALMEX.MX in executive terms."},
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["guardrail_status"] == "llm_not_configured"
    assert payload["llm_enabled"] is False
    assert payload["source_datasets"]
    assert payload["evidence"]


def test_ask_llm_endpoint_rejects_out_of_domain_question(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    response = client.post(
        "/ask-llm",
        json={"question": "Who won the World Cup?"},
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["guardrail_status"] == "blocked_out_of_domain"
    assert payload["llm_enabled"] is False
    assert payload["source_datasets"] == []
    assert payload["evidence"] == []


def test_ask_llm_endpoint_rejects_predictive_question(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    response = client.post(
        "/ask-llm",
        json={"question": "Can you predict next week's price for WALMEX.MX?"},
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["guardrail_status"] == "blocked_predictive_or_advisory"
    assert payload["llm_enabled"] is False
    assert payload["source_datasets"] == []
    assert payload["evidence"] == []
