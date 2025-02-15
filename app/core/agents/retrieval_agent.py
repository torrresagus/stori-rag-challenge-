from typing import Dict, List

from langchain.prompts import ChatPromptTemplate
from langchain_core.documents import Document

from app.constants.openai_models import OpenAIModels
from app.core.agents.base_agent import BaseAgent
from app.utils.logger import logger


class RetrievalAgent(BaseAgent):
    """Agent for handling document retrieval and query responses.

    This agent processes queries against provided documents and generates
    contextual responses with source attribution.
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
                    "You are a retrieval agent that will generate a response to a query based on the documents provided. "
                    "You must retrieve the source of the information from the documents provided and cite it in your response.",
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
        """Generate a response to a query based on the provided documents.

        Args:
            query (str): The user's query
            documents (List[Document]): List of relevant documents

        Returns:
            Dict[str, str]: Response containing the AI's answer

        Raises:
            Exception: If an error occurs during response generation
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
                return {"ia_response": response.content}
            else:
                return {"ia_response": response}
        except Exception as e:
            logger.error("Error generating response: %s", e)
            raise Exception(f"Failed to generate response: {str(e)}") from e

    def _format_documents(self, documents: List[Document]) -> str:
        """Format documents for prompt input.

        Args:
            documents (List[Document]): Documents to format

        Returns:
            str: Formatted document string
        """
        return "\n".join(
            [
                f"Page: {doc.metadata['page']}\nSource: {doc.metadata['file_name']}\n{doc.page_content}\n-----------\n"
                for doc in documents
            ]
        )
