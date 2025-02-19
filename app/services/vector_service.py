import os
from typing import List, Tuple

from fastapi import HTTPException, status
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector

from app.constants.openai_models import EmbeddingOpenAIModels


class VectorService:
    def __init__(
        self,
        collection_name: str,
        embedding_model: EmbeddingOpenAIModels = EmbeddingOpenAIModels.TEXT_EMBEDDING_3_LARGE,
        connection: str = os.getenv("DATABASE_URL"),
    ):
        try:
            self.embeddings = OpenAIEmbeddings(model=embedding_model)
            self.vector_store = PGVector(
                embeddings=self.embeddings,
                collection_name=collection_name,
                connection=connection,
                use_jsonb=True,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error at initializing the vector store with embeddings model '{embedding_model}': {e}",
            )

    def index_documents(
        self, documents: List[Document], ids: List = None
    ) -> None:
        try:
            if not ids:
                ids = [doc.metadata.get("id") for doc in documents]
            self.vector_store.add_documents(documents, ids=ids)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error at indexing the documents: {e}",
            )

    def search(
        self, query: str, k: int = 10, filter_params: dict = None
    ) -> List[Document]:
        try:
            if filter_params:
                return self.vector_store.similarity_search(
                    query, k=k, filter=filter_params
                )
            else:
                return self.vector_store.similarity_search(query, k=k)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while searching documents: {e}",
            )

    def search_with_score(
        self, query: str, k: int = 10, filter_params: dict = None
    ) -> List[Tuple[Document, float]]:
        """
        Perform a similarity search and return documents with their similarity scores.

        Args:
            query (str): The query string.
            k (int, optional): The number of results to return. Defaults to 10.
            filter_params (dict, optional): Filters to apply on document metadata.

        Returns:
            List[Tuple[Document, float]]: Tuples of documents and their similarity scores.
        """
        try:
            if filter_params:
                return self.vector_store.similarity_search_with_score(
                    query, k=k, filter=filter_params
                )
            else:
                return self.vector_store.similarity_search_with_score(
                    query, k=k
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred during search with score: {e}",
            )

    def delete_documents(self, ids: List) -> None:
        """
        Deletes documents from the vector store using their IDs.

        Args:
            ids (List): List of document identifiers to delete.
        """
        try:
            self.vector_store.delete(ids=ids)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting documents: {e}",
            )

    def as_retriever(self, search_kwargs: dict = None):
        return self.vector_store.as_retriever(search_kwargs=search_kwargs)

    def delete_collection(self):
        self.vector_store.delete_collection()
