# app/core/agents/retrieval_agent.py
from typing import Dict, List

from langchain.prompts import ChatPromptTemplate
from langchain_core.documents import Document

from app.constants.openai_models import OpenAIModels
from app.core.agents.base_agent import BaseAgent
from app.utils.logger import logger


class RetrievalAgent(BaseAgent):
    """
    Agent for handling document retrieval and generating query responses.

    This agent uses provided documents to generate a contextual answer and includes source attribution.
    """

    def __init__(self, correlation_id: str = ""):
        super().__init__(
            model_openai=OpenAIModels.GPT_4O_MINI,
            run_name="Retrieval Agent",
            correlation_id=correlation_id,
        )
        self.prompt_template = ChatPromptTemplate(
            [
                (
                    "system",
                    "You are a retrieval agent that generates responses to queries based on the provided documents. "
                    "Extract the source information from the documents and cite it in your response.",
                ),
                ("assistant", "Documents: {documents}"),
                ("user", "Query: {query}"),
            ]
        )

    def generate_response(
        self,
        query: str,
        documents: List[Document],
    ) -> Dict[str, str]:
        """
        Generate a response based on the query and provided documents.

        Args:
            query (str): The user's query.
            documents (List[Document]): Relevant documents for the query.

        Returns:
            Dict[str, str]: A response containing the AI's answer under the key 'ai_response'.

        Raises:
            Exception: If response generation fails.
        """
        try:
            documents_str = self._format_documents(documents)
            input_data = {
                "query": query,
                "documents": documents_str,
            }
            response = self.run(
                self.prompt_template,
                input_data,
            )

            if hasattr(response, "content"):
                return {"ai_response": response.content}
            else:
                return {"ai_response": response}
        except Exception as e:
            logger.error("Error generating response: %s", e)
            raise Exception(f"Failed to generate response: {str(e)}") from e

    def _format_documents(self, documents: List[Document]) -> str:
        """
        Format the documents for prompt input.

        Args:
            documents (List[Document]): Documents to format.

        Returns:
            str: A single formatted string containing all documents.
        """
        return "\n".join(
            [
                f"Page: {doc.metadata['page']}\nSource: {doc.metadata['file_name']}\n{doc.page_content}\n-----------\n"
                for doc in documents
            ]
        )
