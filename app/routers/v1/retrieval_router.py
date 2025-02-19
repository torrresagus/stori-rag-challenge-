# app/routers/v1/retrieval_router.py
from typing import Dict

from fastapi import APIRouter, HTTPException, Path, Query

from app.services import RetrievalService

router = APIRouter(
    prefix="/retrieve",
    tags=["Retrieval - LLM"],
)


@router.get("/tfidf/{index_name}")
async def retrieve_information_tfidf(
    index_name: str = Path(..., description="Index name"),
    query: str = Query(..., description="Search query"),
    k: int = Query(5, description="Number of results to return"),
    session_id: str = Query(..., description="Session ID for chat history"),
) -> Dict[str, str]:
    """
    Retrieve information based on a query from a specific index.

    Args:
        index_name (str): Name of the index to search
        query (str): Search query
        k (int, optional): Number of documents to retrieve. Defaults to 5.

    Returns:
        Dict[str, str]: Response containing the retrieved information

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        return RetrievalService(
            index_name=index_name, session_id=session_id
        ).retrieve_information(query, "tfidf", k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vector/{collection}")
async def retrieve_information_vector(
    collection: str = Path(..., description="Collection (namespace) name"),
    query: str = Query(..., description="Search query"),
    k: int = Query(5, description="Number of results to return"),
    session_id: str = Query(..., description="Session ID for chat history"),
    reranked: bool = Query(True, description="Whether to rerank the results"),
) -> Dict[str, str]:
    """
    Retrieve information based on a query from a vector store collection.

    Args:
        collection (str): The name of the vector store collection.
        query (str): The search query.
        k (int, optional): The number of documents to retrieve. Defaults to 5.

    Returns:
        Dict[str, str]: The response containing the retrieved information.

    Raises:
        HTTPException: If retrieval fails.
    """
    return RetrievalService(
        collection=collection, session_id=session_id
    ).retrieve_information(query, "vector", k, reranked)
