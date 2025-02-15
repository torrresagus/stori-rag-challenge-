from typing import Dict

from app.core.agents.retrieval_agent import RetrievalAgent
from app.services.index_service import IndexService


class RetrievalService:
    """Service for handling document retrieval and query processing.

    This service coordinates between the index service for document retrieval
    and the retrieval agent for generating responses.
    """

    def __init__(self, index_name: str):
        """Initialize the retrieval service.

        Args:
            index_name (str): Name of the index to use
        """
        self.retrieval_agent = RetrievalAgent()
        self.index_service = IndexService()
        self.index_service.load_index(index_name)

    def retrieve_information(self, query: str, k: int = 5) -> Dict[str, str]:
        """Retrieve and process information based on a query.

        Args:
            query (str): The search query
            k (int, optional): Number of documents to retrieve. Defaults to 5.

        Returns:
            Dict[str, str]: Response containing the processed information

        Raises:
            Exception: If retrieval or processing fails
        """
        docs = self.index_service.search(query, k)
        return self.retrieval_agent.generate_response(query, docs)
