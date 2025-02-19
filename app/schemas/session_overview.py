import uuid
from typing import Optional

from pydantic import BaseModel, Field


class SessionOverview(BaseModel):
    session_id: uuid.UUID = Field(
        description="Unique identifier for the session"
    )
    auto_faithfulness: float = Field(
        description="Evaluation score for the faithfulness of the response of the ia in the chat history."
    )
    auto_relevance: float = Field(
        description="Evaluation score for the relevance of the response of the ia in the chat history to the given query."
    )
    auto_correctness: float = Field(
        description="Evaluation score for the factual correctness of the response of the ia in the chat history."
    )
    auto_toxicity: float = Field(
        description="Evaluation score for the toxicity of the response of the ia in the chat history."
    )
    auto_comments: str = Field(
        description="Comments or additional feedback about the response of the ia in the chat history."
    )
    auto_sentiment: str = Field(
        description="Sentiment of the user chat history, either positive, negative or neutral."
    )
    human_faithfulness: float = Field(
        description="Human evaluation score for response faithfulness to source documents"
    )
    human_relevance: float = Field(
        description="Human evaluation score for response relevance to query"
    )
    human_correctness: float = Field(
        description="Human evaluation score for factual correctness of response"
    )
    human_comments: str = Field(
        description="Human evaluation comments and feedback"
    )

    model_config = {
        "from_attributes": True,
    }


class SessionOverviewAI(BaseModel):
    faithfulness_total: int = Field(
        description=(
            "The total number of interactions or questions evaluated for faithfulness, "
            "i.e., whether the model's responses remained truthful and did not include "
            "invented information outside of the provided context."
        )
    )
    faithfulness_positive: int = Field(
        description=(
            "The count of interactions or questions deemed faithful, meaning the responses "
            "did not deviate from the correct or provided information."
        )
    )

    relevance_total: int = Field(
        description=(
            "The total number of interactions or questions evaluated for relevance, "
            "indicating how well the response is related to and properly addresses "
            "the prompt or context."
        )
    )
    relevance_positive: int = Field(
        description=(
            "The count of interactions or questions considered relevant, "
            "i.e., appropriately and coherently responding to the given context."
        )
    )

    correctness_total: int = Field(
        description=(
            "The total number of interactions or questions evaluated for correctness, "
            "i.e., whether the information provided is factually accurate."
        )
    )
    correctness_positive: int = Field(
        description=(
            "The count of interactions or questions that were deemed factually correct, "
            "with no errors or contradictions based on available knowledge."
        )
    )

    toxicity_total: int = Field(
        description=(
            "The total number of interactions or questions evaluated for toxicity, "
            "i.e., whether the response contains harmful or offensive content."
        )
    )

    toxicity_positive: int = Field(
        description=(
            "The count of interactions or questions that were deemed toxic,"
            "i.e., containing harmful, offensive, discriminatory, violent, sexual explicit or inappropriate content."
        )
    )

    sentiment: str = Field(
        description=(
            "The sentiment of the user chat history, either positive, negative or neutral."
        )
    )

    auto_comments: str = Field(
        description=(
            "Automatically generated feedback based on the overall evaluation, "
            "including suggestions or notes on the quality of the responses."
        )
    )


class SessionOverviewHumanUpdate(BaseModel):
    faithfulness: Optional[float] = Field(
        None,
        description="Human evaluation score for response faithfulness to source documents",
    )
    relevance: Optional[float] = Field(
        None,
        description="Human evaluation score for response relevance to query",
    )
    correctness: Optional[float] = Field(
        None,
        description="Human evaluation score for factual correctness of response",
    )
    comments: Optional[str] = Field(
        None, description="Human evaluation comments and feedback"
    )
