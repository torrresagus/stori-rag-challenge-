# app/services/pdf_loader_service.py
import os
import tempfile
from typing import List

from fastapi import HTTPException, UploadFile
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from starlette import status

from app.utils.logger import logger


class PDFLoaderService:
    def __init__(self, files: List[UploadFile]):
        """Initialize PDF loader service.

        Args:
            files (List[UploadFile]): List of PDF files to process.

        Raises:
            HTTPException: If no files are provided or if any file is not a PDF.
        """
        self.files = files
        self.paths = []
        self.docs = []
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )

        if not self.files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files provided",
            )

        for file in self.files:
            if not file.content_type == "application/pdf":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {file.filename} is not a PDF. Only PDF files are allowed.",
                )

        self._create_temp_files()

    def _create_temp_files(self):
        """Create temporary files from uploaded files.

        Raises:
            HTTPException: If there's an error processing the uploaded files.
        """
        try:
            for file in self.files:
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf",
                    prefix=file.filename + "_temp_",
                )
                content = file.file.read()
                temp_file.write(content)
                temp_file.close()
                self.paths.append(temp_file.name)
        except Exception as e:
            self.delete_temp_files()  # Clean up any created files
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing uploaded files: {str(e)}",
            )

    def load_pdfs(self) -> List[Document]:
        """Load and process PDF documents.

        Returns:
            List[Document]: List of processed documents split into chunks.

        Raises:
            HTTPException: If there's an error loading or processing the PDF documents.
        """
        try:
            all_docs = []
            for path in self.paths:
                loader = PyPDFLoader(path)
                docs = loader.load()
                for doc in docs:
                    doc.metadata["file_name"] = (
                        doc.metadata["source"]
                        .split("/")[-1]
                        .split("_temp_")[0]
                    )
                all_docs.extend(docs)
            self.delete_temp_files()
            self.docs = self.text_splitter.split_documents(all_docs)
            return self.docs
        except Exception as e:
            self.delete_temp_files()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error loading PDF documents: {str(e)}",
            )

    def delete_temp_files(self):
        for path in self.paths:
            try:
                os.remove(path)
            except Exception as e:
                logger.error(f"Error deleting temp file {path}: {e}")
