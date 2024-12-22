import logging
import os
import re
import sqlite3
from datetime import datetime, timedelta

from dotenv import load_dotenv
from telegram import ForceReply, Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters, Updater, CallbackContext,
)

from db import init_db
from handlers.listener import listener
from services.check_and_send_messages import check_and_send_messages
from config import TOKEN


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

if not TOKEN:
    raise ValueError("TOKEN environment variable not set")

init_db()


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, listener))

    application.job_queue.run_repeating(callback=check_and_send_messages, interval=60, first=0)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()