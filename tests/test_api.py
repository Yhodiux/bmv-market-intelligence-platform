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
    assert len(payload["supported_questions"]) == 5
