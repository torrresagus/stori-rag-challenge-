from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.db.db import get_db
from app.services.chat_history_service import get_chat_history_by_session

router = APIRouter(prefix="/chat_history", tags=["Chat History"])


@router.get("/{session_id}")
async def get_chat_history(
    session_id: str = Path(...), db: Session = Depends(get_db)
):
    messages = get_chat_history_by_session(session_id, db)
    return messages
