# app/utils/logger.py
import logging
import os
from logging.config import dictConfig

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv(override=True)

LOGGING_LEVEL = os.getenv("LOGGING_LEVEL")
ENVIRONMENT = os.getenv("ENVIRONMENT")


class LogConfig(BaseModel):
    """Logging configuration for the Stori RAG Challenge API using correlation IDs."""

    LOGGER_NAME: str = "StoriRAGChallenge"
    LOG_FORMAT: str = (
        "%(levelprefix)s [%(correlation_id)s] | %(asctime)s | %(message)s"
    )
    LOG_LEVEL: str = LOGGING_LEVEL

    version: int = 1
    disable_existing_loggers: bool = False

    filters: dict = {
        "correlation_id": {
            "()": "asgi_correlation_id.CorrelationIdFilter",
            "uuid_length": 36,
            "default_value": "-",
        }
    }

    # Log formatters
    formatters: dict = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }

    # Handlers
    handlers: dict = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
            "filters": ["correlation_id"],
        },
    }

    # Loggers
    loggers: dict = {
        LOGGER_NAME: {"handlers": ["default"], "level": LOG_LEVEL},
    }


# Apply the configuration with dictConfig
dictConfig(LogConfig().model_dump())
logger = logging.getLogger("StoriRAGChallenge")
