from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Chat HTML"])


@router.get("/chat", response_class=HTMLResponse)
async def get_chat_html():
    """
    Returns the chat interface HTML page.
    """
    html_file = Path("./app/docs/chat.html")
    return html_file.read_text()
