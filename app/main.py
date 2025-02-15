# app/main.py
from asgi_correlation_id import CorrelationIdMiddleware
from dotenv import load_dotenv
from fastapi import FastAPI

from app.routers.v1 import (
    index_router,
    retrieval_router,
    root_router,
    vector_router,
)

load_dotenv(override=True)

app = FastAPI(
    title="Stori RAG Challenge",
    version="1.0.0",
)
app.add_middleware(CorrelationIdMiddleware)

app.include_router(root_router)
app.include_router(index_router)
app.include_router(vector_router)
app.include_router(retrieval_router)
