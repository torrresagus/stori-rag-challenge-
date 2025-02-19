from dotenv import load_dotenv
from langchain_cohere import CohereRerank

from app.services.vector_service import VectorService
from app.utils.logger import logger

load_dotenv(override=True)


class RerankService:
    def __init__(self, vector_service: VectorService):
        self.vector_service = vector_service
        self.reranker = CohereRerank(model="rerank-multilingual-v3.0", top_n=4)

    def get_documents(self, query: str, k: int):
        documents = self.vector_service.search(query, k)
        return documents

    def search_with_rerank(self, query: str, k: int):
        logger.info("Searching with rerank")
        documents = self.get_documents(query, k)

        print(documents)
        reranked_docs = self.reranker.rerank(documents, query, top_n=3)

        for info in reranked_docs:
            idx = info["index"]
            score = info["relevance_score"]
            documents[idx].metadata["relevance_score"] = score

        reranked_documents = [
            documents[info["index"]] for info in reranked_docs
        ]
        return reranked_documents
