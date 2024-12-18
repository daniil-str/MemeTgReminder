__author__ = 'Danya'

import logging
import os
import re
import sqlite3
from datetime import datetime

from dotenv import load_dotenv
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


load_dotenv()
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN environment variable not set")

# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

insert_query = """
INSERT INTO users (message_id, chat_id, user_id) VALUES (?, ?, ?);
"""

TIME_PATTERN = re.compile(r"\d{2}:\d{2}")

async def listener(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message

    if re.fullmatch(TIME_PATTERN, msg.text):
        message_id = msg.message_id + 1
        chat_id = msg.chat_id
        usr_id = msg.from_user.id
        time = msg.text

        connection = sqlite3.connect("mydatabase.db")
        cursor = connection.cursor()

        cursor.execute(insert_query, [(message_id, chat_id, usr_id, time)][0])
        connection.commit()
        cursor.close()
        connection.close()

def check_and_send_messages():
    conn = sqlite3.connect("mydatabase.db")
    cursor = conn.cursor()

    current_time = datetime.now().strftime("%H:%M")

    cursor.execute("SELECT chat_id, message_id, user_id, time FROM messages")
    rows = cursor.fetchall()

    for chat_id, message_id, user_id, message_time in rows:
        if current_time == message_time:
            forward_message(chat_id, message_id, user_id)
            logging.info(f"Сообщение {message_id} отправлено пользователю {user_id} в {message_time}")

    # Закрываем соединение с базой данных
    conn.close()


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, listener))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()