# app/routers/v1/index_router.py
from typing import List

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from starlette import status

from app.services import IndexService, PDFLoaderService
from app.utils.logger import logger

router = APIRouter(
    prefix="/index",
    tags=["Index"],
)


@router.post(
    "/",
    description="Index documents",
    status_code=status.HTTP_201_CREATED,
)
async def index_documents(
    index_name: str = Form(...),
    files: List[UploadFile] = File(...),
):
    """Create a new document index.

    Args:
        index_name (str): Name of the index to create.
        files (List[UploadFile]): List of PDF files to process and index.

    Returns:
        dict: Status message with index creation result.

    Raises:
        HTTPException: If there's an error processing files or creating the index.
    """
    try:
        pdf_loader_service = PDFLoaderService(files)
        docs = pdf_loader_service.load_pdfs()

        index_service = IndexService(docs)
        index_service.save_index(index_name)

        return {
            "status": "success",
            "message": "Index created successfully",
            "index_name": index_name,
        }
    except HTTPException as e:
        logger.error(f"Error indexing documents: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error indexing documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get(
    "/{index_name}/search",
    description="Search for documents in an index",
    status_code=status.HTTP_200_OK,
)
async def search_index(
    index_name: str,
    query: str,
    k: int = 10,
):
    """Search for documents in an existing index.

    Args:
        index_name (str): Name of the index to search in.
        query (str): Search query string.
        k (int, optional): Number of results to return. Defaults to 10.

    Returns:
        List[Document]: List of relevant documents matching the query.

    Raises:
        HTTPException: If the index is not found or if there's an error during search.
    """
    try:
        index_service = IndexService()
        index_service.load_index(index_name)
        return index_service.search(query, k)
    except HTTPException as e:
        logger.error(f"Error searching index: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error searching index: {e}")
        raise e


@router.delete(
    "/{index_name}",
    description="Delete an index",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_index(index_name: str):
    """Delete an existing index.

    Args:
        index_name (str): Name of the index to delete.

    Returns:
        dict: Status message confirming index deletion.

    Raises:
        HTTPException: If the index is not found or if there's an error during deletion.
    """
    try:
        index_service = IndexService()
        index_service.remove_index(index_name)
        return {
            "status": "success",
            "message": "Index deleted successfully",
        }
    except HTTPException as e:
        logger.error(f"Error deleting index: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error deleting index: {e}")
        raise e
