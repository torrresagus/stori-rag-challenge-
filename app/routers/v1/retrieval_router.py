from typing import Dict, Optional

from fastapi import APIRouter, HTTPException

from app.services.retrieval_service import RetrievalService

router = APIRouter()


@router.get("/retrieve")
async def retrieve_information(
    index_name: str, query: str, k: Optional[int] = 5
) -> Dict[str, str]:
    """Retrieve information based on a query from a specific index.

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
        return RetrievalService(index_name=index_name).retrieve_information(
            query, k
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
