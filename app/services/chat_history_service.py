import uuid

from sqlalchemy import text
from sqlalchemy.orm import Session


def get_chat_history_by_session(session_id: str, db: Session):

    session_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, session_id)

    query = text(
        """
        SELECT session_id, message, created_at
        FROM chat_history
        WHERE session_id = :session_id
        ORDER BY created_at ASC
    """
    )
    # Ejecuta la consulta
    result = db.execute(query, {"session_id": session_uuid}).fetchall()

    messages = []
    for row in result:
        json_message = row.message
        if isinstance(json_message, dict) and "data" in json_message:
            message_type = json_message["data"].get("type")
            content = json_message["data"].get("content")
        else:
            message_type = None
            content = None

        messages.append(
            {
                "type": message_type,
                "content": content,
                "created": row.created_at,
                "session_id": row.session_id,
            }
        )

    return messages
