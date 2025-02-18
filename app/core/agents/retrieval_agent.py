# app/core/agents/retrieval_agent.py
import os
import uuid
from typing import Dict, List

import psycopg
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.prompts import MessagesPlaceholder
from langchain_postgres import PostgresChatMessageHistory

from app.constants.openai_models import OpenAIModels
from app.core.agents.base_agent import BaseAgent
from app.utils.db_utils import ensure_chat_history_table_exists

load_dotenv(override=True)


class RetrievalAgent(BaseAgent):
    """
    Retrieval agent that generates responses based on documents
    and uses memory (chat history) to maintain context.
    """

    def __init__(self, correlation_id: str = "", session_id: str = ""):
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
            run_name="Retrieval Agent",
            correlation_id=correlation_id,
            session_id=session_id,
            chat_history=chat_history,
        )

        self.prompt_template = ChatPromptTemplate(
            [
                (
                    "system",
                    "You are a retrieval agent that generates responses to queries based on the provided documents. "
                    "Extract the source information from the documents and cite it in your response.",
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "Documents: {documents}"),
                ("user", "Query: {query}"),
            ]
        )

    def generate_response(
        self,
        query: str,
        documents: List[Document],
    ) -> Dict[str, str]:
        """
        Generates a response based on the provided query and documents.

        Args:
            query (str): The user's query.
            documents (List[Document]): List of relevant documents.

        Returns:
            Dict[str, str]: The agent's response under the 'ai_response' key.
        """
        documents_str = self._format_documents(documents)
        input_data = {
            "query": query,
            "documents": documents_str,
        }
        response = self.chat(
            self.prompt_template, input_data, user_message=query
        )

        message_content = (
            response.content if hasattr(response, "content") else response
        )
        return {"ai_response": message_content}

    def _format_documents(self, documents: List[Document]) -> str:
        """
        Formats the documents to be used in the prompt.

        Args:
            documents (List[Document]): List of documents.

        Returns:
            str: Formatted string with the information of the documents.
        """
        formatted_docs = []
        for i, doc in enumerate(documents):
            doc_str = f"Document {i+1}:\n"

            if hasattr(doc, "metadata"):
                if "page" in doc.metadata:
                    doc_str += f"Page: {doc.metadata['page']}\n"
                if "relevance_score" in doc.metadata:
                    doc_str += (
                        f"Relevance Score: {doc.metadata['relevance_score']}\n"
                    )
                if "file_name" in doc.metadata:
                    doc_str += f"Source: {doc.metadata['file_name']}\n"

            doc_str += "\n"

            if hasattr(doc, "page_content") and doc.page_content:
                doc_str += f"{doc.page_content}"
            else:
                doc_str += "No content available"

            formatted_docs.append(doc_str)

        return f"\n{'-' * 100}\n".join(formatted_docs)
