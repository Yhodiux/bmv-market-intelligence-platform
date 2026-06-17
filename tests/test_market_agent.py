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

    assert "only answer supported" in response["answer"]
    assert response["data_points"] == []
    assert response["source_datasets"] == []
    assert response["supported_questions"] == SUPPORTED_QUESTIONS
