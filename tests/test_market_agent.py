from src.ai_agent.market_agent import SUPPORTED_QUESTIONS, answer_question


def test_agent_answers_supported_questions_with_sources_and_data() -> None:
    for question in SUPPORTED_QUESTIONS:
        response = answer_question(question)

        assert response["question"] == question
        assert response["answer"]
        assert response["source_datasets"]
        assert response["data_points"]
        assert response["supported_questions"] == SUPPORTED_QUESTIONS


def test_agent_rejects_unsupported_questions_without_data() -> None:
    response = answer_question("Can you predict tomorrow's exchange rate?")

    assert "cannot provide forecasts" in response["answer"]
    assert response["data_points"] == []
    assert response["source_datasets"] == []
    assert response["supported_questions"] == SUPPORTED_QUESTIONS


def test_agent_rejects_out_of_domain_questions_without_data() -> None:
    response = answer_question("Who won the World Cup?")

    assert "governed market intelligence" in response["answer"]
    assert response["data_points"] == []
    assert response["source_datasets"] == []
    assert response["supported_questions"] == SUPPORTED_QUESTIONS


def test_agent_answers_issuer_summary() -> None:
    response = answer_question("Summarize WALMEX.MX.")

    assert response["source_datasets"] == ["gold_performance", "gold_volatility", "gold_liquidity"]
    assert len(response["data_points"]) == 1
    assert response["data_points"][0]["ticker"] == "WALMEX.MX"


def test_agent_compares_two_issuers() -> None:
    response = answer_question("Compare WALMEX.MX and CEMEXCPO.MX.")

    assert response["source_datasets"] == ["gold_performance", "gold_volatility", "gold_liquidity"]
    assert len(response["data_points"]) == 2
    assert {record["ticker"] for record in response["data_points"]} == {"WALMEX.MX", "CEMEXCPO.MX"}


def test_agent_answers_market_snapshot() -> None:
    response = answer_question("Show me the latest market snapshot.")

    assert response["source_datasets"] == ["gold_performance", "gold_volatility", "gold_liquidity"]
    assert len(response["data_points"]) == 1
    assert response["data_points"][0]["issuer_count"] > 0
