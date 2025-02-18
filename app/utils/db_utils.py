# app/utils/db_utils.py
from langchain_postgres import PostgresChatMessageHistory

from app.utils.logger import logger


def ensure_chat_history_table_exists(
    sync_connection, table_name="chat_history"
):
    try:
        with sync_connection.cursor() as cursor:
            cursor.execute(
                "SELECT to_regclass(%s);", (f"public.{table_name}",)
            )
            exists = cursor.fetchone()[0]
            if exists is None:
                PostgresChatMessageHistory.create_tables(
                    sync_connection, table_name
                )
    except Exception as e:
        logger.error(f"Error at ensure_chat_history_table_exists: {e}")
        raise
