# app/main.py
import os

from asgi_correlation_id import CorrelationIdMiddleware
from dotenv import load_dotenv
from fastapi import FastAPI

from app.routers import get_swagger_router
from app.routers.v1 import (
    index_router,
    retrieval_router,
    root_router,
    vector_router,
)
from app.utils.logger import logger

load_dotenv(override=True)

if os.getenv("ENVIRONMENT") == "local":
    logger.warning("Running in local mode, swagger has no auth")
else:
    logger.info("Running in non-local mode, swagger has auth")


app = FastAPI(
    title="Stori RAG Challenge",
    version="1.0.0",
    docs_url=None if os.getenv("ENVIRONMENT") != "local" else "/docs",
    redoc_url=None if os.getenv("ENVIRONMENT") != "local" else "/redoc",
    openapi_url=(
        None if os.getenv("ENVIRONMENT") != "local" else "/openapi.json"
    ),
)
app.add_middleware(CorrelationIdMiddleware)

app.include_router(get_swagger_router(app))
app.include_router(root_router)
app.include_router(index_router)
app.include_router(vector_router)
app.include_router(retrieval_router)
