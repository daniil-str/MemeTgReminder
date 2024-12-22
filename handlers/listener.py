import logging
import re
import sqlite3

from telegram import Update
from telegram.ext import ContextTypes

from config import BASE_DIR

TIME_PATTERN = re.compile(r"\d{2}:\d{2}")


insert_query = """
insert into messages (message_id, chat_id, user_id, time_of_day) values (?, ?, ?, ?);
"""

async def listener(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message

    if re.fullmatch(TIME_PATTERN, msg.text):
        message_id = msg.message_id + 1
        chat_id = msg.chat_id
        usr_id = msg.from_user.id
        time_of_day = msg.text

        connection = sqlite3.connect(BASE_DIR / "mydatabase.db")
        cursor = connection.cursor()

        cursor.execute(insert_query, [(message_id, chat_id, usr_id, time_of_day)][0])
        logging.info(f"Сообщение {message_id} записано в базу, время {time_of_day}")

        connection.commit()
        cursor.close()
        connection.close()