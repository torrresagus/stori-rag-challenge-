from dotenv import load_dotenv
from langchain.retrievers.contextual_compression import (
    ContextualCompressionRetriever,
)
from langchain_cohere import CohereRerank

from app.services.vector_service import VectorService

load_dotenv(override=True)


class RerankService:
    def __init__(self, vector_service: VectorService):
        self.retriever = vector_service.as_retriever(search_kwargs={"k": 20})
        self.compressor = CohereRerank(model="rerank-v3.5", top_n=4)
        self.compression_retriever = ContextualCompressionRetriever(
            base_compressor=self.compressor, base_retriever=self.retriever
        )

    def search_with_rerank(self, query: str, k: int):
        self.compressor.top_n = k
        compressed_docs = self.compression_retriever.invoke(query)
        return compressed_docs
