from typing import List

from fastapi import (
    APIRouter,
    Body,
    File,
    Form,
    HTTPException,
    Path,
    Query,
    UploadFile,
)
from pydantic import BaseModel
from starlette import status

from app.constants.openai_models import EmbeddingOpenAIModels
from app.services import PDFLoaderService, VectorService

router = APIRouter(
    prefix="/vector",
    tags=["Vector - Vector Store"],
)


class DeleteDocumentsRequest(BaseModel):
    ids: List[int]


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    description="Index documents using vector service",
)
async def index_documents_vector(
    collection_name: str = Form(...),
    files: List[UploadFile] = File(...),
):
    """
    Index documents using the vector service for a specified collection.

    Args:
        collection_name (str): The name of the collection (namespace) for documents.
        files (List[UploadFile]): List of PDF files to process and index.

    Returns:
        dict: A status message indicating the result of indexing.

    Raises:
        HTTPException: If an error occurs during file processing or indexing.
    """
    try:
        pdf_loader_service = PDFLoaderService(files)
        docs = pdf_loader_service.load_pdfs()

        vector_service = VectorService(
            collection_name=collection_name,
            embedding_model=EmbeddingOpenAIModels.TEXT_EMBEDDING_3_LARGE,
        )
        vector_service.index_documents(docs)

        return {
            "status": "success",
            "message": "Documents indexed successfully",
            "collection_name": collection_name,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get(
    "/{collection}/search",
    status_code=status.HTTP_200_OK,
    description="Search for documents in a vector store",
)
async def search_vector(
    collection: str = Path(..., description="Collection (namespace) name"),
    query: str = Query(..., description="Search query"),
    k: int = Query(10, description="Number of results to return"),
):
    """
    Search for documents in the specified collection using a similarity search.

    Args:
        collection (str): The collection (namespace) name.
        query (str): The search query.
        k (int, optional): The number of results to return. Defaults to 10.

    Returns:
        dict: A dictionary containing the status and search results.

    Raises:
        HTTPException: If an error occurs during the search.
    """
    try:
        vector_service = VectorService(
            collection_name=collection,
            embedding_model=EmbeddingOpenAIModels.TEXT_EMBEDDING_3_LARGE,
        )
        documents = vector_service.search(query, k)
        results = [
            {"page_content": doc.page_content, "metadata": doc.metadata}
            for doc in documents
        ]
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get(
    "/{collection}/search_with_score",
    status_code=status.HTTP_200_OK,
    description="Search for documents in a vector store and include similarity scores",
)
async def search_vector_with_score(
    collection: str = Path(..., description="Collection (namespace) name"),
    query: str = Query(..., description="Search query"),
    k: int = Query(10, description="Number of results to return"),
):
    """
    Search for documents in the specified collection with their similarity scores.

    Args:
        collection (str): The collection (namespace) name.
        query (str): The search query.
        k (int, optional): The number of results to return. Defaults to 10.

    Returns:
        list: A list of documents with their corresponding similarity scores.

    Raises:
        HTTPException: If an error occurs during the search.
    """
    try:
        vector_service = VectorService(
            collection_name=collection,
            embedding_model=EmbeddingOpenAIModels.TEXT_EMBEDDING_3_LARGE,
        )
        return vector_service.search_with_score(query, k)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete(
    "/{collection}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete documents from a vector store by their IDs",
)
async def delete_documents_vector(
    collection: str = Path(..., description="Collection (namespace) name"),
    deletion_request: DeleteDocumentsRequest = Body(...),
):
    """
    Delete documents from the vector store using their IDs.

    Args:
        collection (str): The collection (namespace) name.
        deletion_request (DeleteDocumentsRequest): Data model containing document IDs.

    Raises:
        HTTPException: If document IDs are not provided or deletion fails.
    """
    if deletion_request is None or not deletion_request.ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document IDs are required",
        )
    try:
        vector_service = VectorService(
            collection_name=collection,
            embedding_model=EmbeddingOpenAIModels.TEXT_EMBEDDING_3_LARGE,
        )
        vector_service.delete_documents(deletion_request.ids)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
