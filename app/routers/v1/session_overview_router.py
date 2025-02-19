from typing import List

from fastapi import (
    APIRouter,
    Body,
    Depends,
    Form,
    HTTPException,
    Query,
    Response,
)
from sqlalchemy.orm import Session
from starlette import status

from app.db.db import get_db
from app.schemas.session_overview import (
    SessionOverview,
    SessionOverviewHumanUpdate,
)
from app.services import SessionOverviewService

router = APIRouter(
    prefix="/session_overview",
    tags=["Session Overview"],
)


@router.post(
    "/",
    description="Run automated evaluation of the session (creates new overview or updates existing one)",
)
async def evaluate_session(
    session_id: str = Form(...),
    db: Session = Depends(get_db),
    response: Response = None,
):
    """
    Process a session evaluation request.

    Depending on whether a session overview already exists, the endpoint creates a new record
    (HTTP 201 Created) or updates the existing one (HTTP 202 Accepted).

    Args:
        session_id (str): Unique session identifier from the form data.
        db (Session): Database session dependency.
        response (Response): Response object to set status code.

    Returns:
        dict: A JSON response with the evaluation result.
    """
    try:
        service = SessionOverviewService(session_id)
        session_overview, created = service.evaluate_session(db)

        if created:
            response.status_code = status.HTTP_201_CREATED
            message = "Session overview created successfully"
        else:
            response.status_code = status.HTTP_202_ACCEPTED
            message = "Session overview updated successfully"

        return {
            "status": "success",
            "message": message,
            "session_overview": session_overview,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    description="Get session overviews with pagination and optional filtering by session_id",
)
async def get_session_overviews(
    limit: int = Query(10, gt=0, description="Number of items per page"),
    cursor: int = Query(
        None,
        description="Cursor (last session overview id from previous page)",
    ),
    session_id: str = Query(
        None, description="Optional session id to filter results"
    ),
    db: Session = Depends(get_db),
):
    try:
        service = SessionOverviewService()
        session_overviews = service.get_session_overviews(
            db, limit, cursor, session_id
        )
        session_overviews_data = [
            SessionOverview.model_validate(so) for so in session_overviews
        ]
        return {"status": "success", "data": session_overviews_data}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.patch(
    "/{session_id}",
    status_code=status.HTTP_202_ACCEPTED,
    description="Update human evaluation fields of a session overview",
)
async def update_session_overview(
    session_id: str,
    update_data: SessionOverviewHumanUpdate,
    db: Session = Depends(get_db),
):
    try:
        service = SessionOverviewService(session_id)
        updated_session_overview = service.update_human_fields(
            session_id, update_data, db
        )
        return {
            "status": "success",
            "message": "Session overview updated successfully",
            "session_overview": updated_session_overview,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post(
    "/questions-dataset",
    status_code=status.HTTP_200_OK,
    description="Upload a dataset of questions and their correct answers to be stored as ground truth",
)
async def upload_questions_dataset(
    questions_dataset: List[dict] = Body(...),
):
    try:
        service = SessionOverviewService()
        service.upload_questions_dataset(questions_dataset)
        return {
            "status": "success",
            "message": "Questions dataset uploaded successfully",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
