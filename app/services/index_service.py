# app/services/index_service.py
import os
import shutil
from typing import List

from fastapi import HTTPException
from langchain_community.retrievers import TFIDFRetriever
from langchain_core.documents import Document
from starlette import status


class IndexService:
    """Service for managing TF-IDF based document retrieval.

    This service provides functionality to create, save, load, and search through documents
    using TF-IDF (Term Frequency-Inverse Document Frequency) retrieval method.
    """

    def __init__(self, documents: List[Document] = None):
        """Initialize the index service.

        Args:
            documents (List[Document], optional): List of documents to initialize the retriever. Defaults to None.
        """
        self.retriever = None
        if documents:
            self.retriever = TFIDFRetriever.from_documents(documents)

    def index_documents(self, documents: List[Document]) -> None:
        """Create a new index from a list of documents.

        Args:
            documents (List[Document]): List of documents to index.
        """
        self.retriever = TFIDFRetriever.from_documents(documents)

    def save_index(self, name: str) -> None:
        """Save the current retriever to a local file.

        Args:
            name (str): Name of the index file.

        Raises:
            HTTPException: If no retriever has been initialized or if there's an error saving the index.
        """
        if not self.retriever:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No index has been created yet",
            )
        try:
            self.retriever.save_local(f"./app/indexes/{name}.pkl")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error saving index: {str(e)}",
            )

    def load_index(self, name: str) -> None:
        """Load a previously saved retriever from a local file.

        Args:
            name (str): Name of the index file to load.

        Raises:
            HTTPException: If the index file is not found.
        """
        try:
            self.retriever = TFIDFRetriever.load_local(
                f"./app/indexes/{name}.pkl",
                allow_dangerous_deserialization=True,
            )
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Index {name} not found",
            )

    def search(self, query: str, k: int = 10) -> List[Document]:
        """Search for relevant documents using the query.

        Args:
            query (str): The search query string.
            k (int, optional): Number of results to return. Defaults to 10.

        Returns:
            List[Document]: List of relevant documents matching the query.

        Raises:
            HTTPException: If no index exists or if the search operation fails.
        """
        if not self.retriever:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No index has been created yet",
            )
        try:
            self.retriever.k = k
            return self.retriever.invoke(query)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error performing search: {str(e)}",
            )

    def remove_index(self, name: str) -> None:
        """Remove a previously saved retriever file.

        Args:
            name (str): Name of the index file to remove.

        Raises:
            HTTPException: If the index is not found or if there's an error during removal.
        """
        try:
            index_path = f"./app/indexes/{name}.pkl"
            if os.path.isdir(index_path):
                shutil.rmtree(index_path)
            else:
                os.remove(index_path)
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Index {name} not found",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error removing index: {e}",
            )
