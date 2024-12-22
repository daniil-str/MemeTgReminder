import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


TOKEN = os.getenv("TOKEN")

BASE_DIR = Path(__file__).resolve().parent