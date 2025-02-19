# app/core/agents/retrieval_agent.py
import os
import uuid

import psycopg
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langchain_postgres import PostgresChatMessageHistory

from app.constants.openai_models import EmbeddingOpenAIModels, OpenAIModels
from app.core.agents.base_agent import BaseAgent
from app.schemas.session_overview import SessionOverviewAI
from app.services.vector_service import VectorService
from app.utils.db_utils import ensure_chat_history_table_exists

load_dotenv(override=True)


class SessionAnalysisAgent(BaseAgent):
    """
    SessionAnalysisAgent uses chat history and vector search to evaluate a session
    against a ground truth and return structured automated evaluation results.
    """

    def __init__(self, correlation_id: str = "", session_id: str = ""):
        """
        Initialize the SessionAnalysisAgent.

        Args:
            correlation_id (str): Unique correlation identifier.
            session_id (str): Unique session identifier.
        """
        sync_connection = psycopg.connect(os.getenv("DATABASE_URL"))
        ensure_chat_history_table_exists(sync_connection)

        session_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, session_id)

        chat_history = PostgresChatMessageHistory(
            "chat_history",
            str(session_uuid),
            sync_connection=sync_connection,
        )

        super().__init__(
            model_openai=OpenAIModels.GPT_4O_MINI,
            run_name="Session Analysis Agent",
            correlation_id=correlation_id,
            chat_history=chat_history,
            structured_output=SessionOverviewAI,
        )

        self.messages = self.chat_history.messages
        self.prompt_template = ChatPromptTemplate(
            [
                (
                    "system",
                    "You are a session analysis agent that evaluates chat conversations. "
                    "You will receive: "
                    "- A conversation between a user (and possibly the model) that includes multiple messages. "
                    "- A ground truth (verified sources or evidence) to compare against the information presented in the conversation. "
                    "Your task is to evaluate the entire conversation (all relevant turns) against the ground truth and produce a JSON object with the structure and fields described.",
                ),
                ("assistant", "Ground Truth: {ground_truth}"),
                ("assistant", "Session History to evaluate: {chat_history}"),
            ]
        )

        self.vector_service = VectorService(
            collection_name="questions_dataset",
            embedding_model=EmbeddingOpenAIModels.TEXT_EMBEDDING_3_LARGE,
        )

    def get_ground_truth(self):
        """
        Extract ground truth documents by searching based on human messages in the chat history.

        Returns:
            list: A list of search results representing ground truth documents.
        """
        ground_truth = []
        for message in self.messages:
            if isinstance(message, HumanMessage):
                ground_truth.append(
                    self.vector_service.search(query=message.content, k=2)
                )
        return ground_truth

    def evaluate_session(self) -> SessionOverviewAI:
        """
        Evaluate the session using automated methods and return the structured evaluation.

        Returns:
            SessionOverviewAI: The automated evaluation result.
        """
        ground_truth = self.get_ground_truth()
        input_data = {
            "chat_history": self.messages,
            "ground_truth": ground_truth,
        }
        return self.run(self.prompt_template, input_data)
