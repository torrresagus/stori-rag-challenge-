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

    This service provides functionality to create, save, load, and search through a TF-IDF index.
    """

    def __init__(self, documents: List[Document] = None):
        """Initialize the TF-IDF index service.

        Args:
            documents (List[Document], optional): Documents used to initialize the index. Defaults to None.
        """
        self.retriever = None
        if documents:
            self.retriever = TFIDFRetriever.from_documents(documents)

    def index_documents(self, documents: List[Document]) -> None:
        """Create a TF-IDF index from the provided documents.

        Args:
            documents (List[Document]): Documents to index.
        """
        self.retriever = TFIDFRetriever.from_documents(documents)

    def save_index(self, name: str) -> None:
        """Save the current TF-IDF index to a local file.

        Args:
            name (str): The base name of the index file.

        Raises:
            HTTPException: If no index has been created or if an error occurs while saving.
        """
        if not self.retriever:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No index has been created yet.",
            )
        try:
            self.retriever.save_local(f"./app/indexes/{name}.pkl")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error saving index: {str(e)}",
            )

    def load_index(self, name: str) -> None:
        """Load an existing TF-IDF index from a local file.

        Args:
            name (str): The base name of the index file to load.

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
        """Search for relevant documents using the TF-IDF index.

        Args:
            query (str): The search query.
            k (int, optional): The number of results to return. Defaults to 10.

        Returns:
            List[Document]: Documents matching the query.

        Raises:
            HTTPException: If no index exists or if an error occurs during the search.
        """
        if not self.retriever:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No index has been created yet.",
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
        """Remove a saved TF-IDF index file.

        Args:
            name (str): The base name of the index file to remove.

        Raises:
            HTTPException: If the index file is not found or removal fails.
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
