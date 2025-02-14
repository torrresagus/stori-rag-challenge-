# app/main.py
import os

from asgi_correlation_id import CorrelationIdMiddleware
from dotenv import load_dotenv
from fastapi import FastAPI

from app.routers.v1 import index_router, root_router
from app.utils.logger import logger

load_dotenv(override=True)

app = FastAPI(
    title="Stori RAG Challenge",
    version="1.0.0",
)
app.add_middleware(CorrelationIdMiddleware)

app.include_router(root_router)
app.include_router(index_router)
