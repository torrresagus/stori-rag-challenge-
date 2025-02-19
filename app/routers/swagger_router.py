# app/routers/swagger_controller.py
import os

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.security import HTTPBasic, HTTPBasicCredentials

load_dotenv(override=True)

security = HTTPBasic()

USERNAME = os.getenv("SWAGGER_USERNAME")
PASSWORD = os.getenv("SWAGGER_PASSWORD")


def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != USERNAME or credentials.password != PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def get_swagger_router(app):
    swagger_router = APIRouter()

    @swagger_router.get("/docs", include_in_schema=False)
    def custom_docs(credentials: HTTPBasicCredentials = Depends(authenticate)):
        return get_swagger_ui_html(
            openapi_url="/openapi.json", title="Talent Connection API"
        )

    @swagger_router.get("/openapi.json", include_in_schema=False)
    def openapi_json(
        credentials: HTTPBasicCredentials = Depends(authenticate),
    ):
        return app.openapi()

    return swagger_router
