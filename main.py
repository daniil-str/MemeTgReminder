__author__ = 'Danya'

import logging
import os
import re
import sqlite3
from datetime import datetime

from dotenv import load_dotenv
from telegram import ForceReply, Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters, Updater, CallbackContext,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


load_dotenv()
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN environment variable not set")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    ...

insert_query = """
INSERT INTO users (message_id, chat_id, user_id, time_of_day) VALUES (?, ?, ?, ?);
"""

TIME_PATTERN = re.compile(r"\d{2}:\d{2}")

async def listener(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message

    if re.fullmatch(TIME_PATTERN, msg.text):
        message_id = msg.message_id + 1
        chat_id = msg.chat_id
        usr_id = msg.from_user.id
        time_of_day = msg.text

        connection = sqlite3.connect("mydatabase.db")
        cursor = connection.cursor()

        cursor.execute(insert_query, [(message_id, chat_id, usr_id, time_of_day)][0])
        connection.commit()
        cursor.close()
        connection.close()

async def check_and_send_messages(context: CallbackContext) -> None:
    conn = sqlite3.connect("mydatabase.db")
    cursor = conn.cursor()

    current_time = datetime.now().strftime("%H:%M")

    cursor.execute("SELECT chat_id, message_id, user_id, time_of_day FROM users")
    rows = cursor.fetchall()

    for chat_id, message_id, user_id, message_time in rows:
        if current_time == message_time:
            bot = context.bot
            await bot.forward_message(
                chat_id=chat_id,
                message_id=message_id,
                from_chat_id=chat_id)
            logging.info(f"Сообщение {message_id} из чата {chat_id} в чат {user_id}")

            cursor.execute("delete from users where message_id = ?", (message_id,))
            conn.commit()

    conn.close()


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, listener))

    application.job_queue.run_repeating(callback=check_and_send_messages, interval=60, first=0)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()