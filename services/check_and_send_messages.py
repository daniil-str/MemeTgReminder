import logging
import sqlite3
from datetime import datetime, timedelta

from telegram.ext import CallbackContext

from config import BASE_DIR


async def check_and_send_messages(context: CallbackContext) -> None:
    conn = sqlite3.connect(BASE_DIR / "mydatabase.db")
    cursor = conn.cursor()

    # время сервера отличается от Московского
    current_time = (datetime.now() + timedelta(hours=3)).strftime("%H:%M")

    cursor.execute("SELECT chat_id, message_id, user_id, time_of_day FROM messages")
    rows = cursor.fetchall()

    for chat_id, message_id, user_id, message_time in rows:
        if current_time == message_time:
            bot = context.bot
            await bot.forward_message(
                chat_id=chat_id,
                message_id=message_id,
                from_chat_id=chat_id)
            logging.info(f"Сообщение {message_id} отправлено из чата {chat_id} в чат {user_id}")

            cursor.execute("delete from messages where message_id = ?", (message_id,))
            conn.commit()

    conn.close()