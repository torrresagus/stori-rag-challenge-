# app/services/retrieval_service.py
from typing import Dict

from langchain_openai import OpenAIEmbeddings

from app.constants.openai_models import EmbeddingOpenAIModels
from app.core.agents.retrieval_agent import RetrievalAgent
from app.services.index_service import IndexService
from app.services.rerank_service import RerankService
from app.services.vector_service import VectorService


class RetrievalService:
    """
    Service for handling document retrieval and query processing.

    This service coordinates between either a TF-IDF index or a vector store for document retrieval
    and the retrieval agent for generating the response.
    """

    def __init__(
        self,
        index_name: str = None,
        collection: str = None,
        session_id: str = None,
    ):
        """
        Initialize the retrieval service.

        Args:
            index_name (str, optional): Name of the TF-IDF index to use.
            collection (str, optional): Name of the vector store collection to use.
            session_id (str, optional): Session ID for chat history.
        """
        self.retrieval_agent = RetrievalAgent(session_id=session_id)
        self.index_service = IndexService()
        if index_name:
            self.index_service.load_index(index_name)
        if collection:
            self.vector_service = VectorService(
                collection_name=collection,
                embedding_model=EmbeddingOpenAIModels.TEXT_EMBEDDING_3_LARGE,
            )
            self.rerank_service = RerankService(self.vector_service)

    def retrieve_information(
        self,
        query: str,
        retrieval_type: str,
        k: int = 5,
        reranked: bool = True,
    ) -> Dict[str, str]:
        """
        Retrieve and process information based on a query.

        Args:
            query (str): The search query.
            retrieval_type (str): The retrieval method to use ('tfidf' or 'vector').
            k (int, optional): The number of documents to retrieve. Defaults to 5.

        Returns:
            Dict[str, str]: The response produced by the retrieval agent.

        Raises:
            Exception: If retrieval or response generation fails.
        """
        if retrieval_type == "tfidf":
            docs = self.index_service.search(query, k)
        elif retrieval_type == "vector":
            docs = (
                self.rerank_service.search_with_rerank(query, k)
                if reranked
                else self.vector_service.search(query, k)
            )
        else:
            raise Exception(f"Unsupported retrieval type: {retrieval_type}")
        return self.retrieval_agent.generate_response(query, docs)
