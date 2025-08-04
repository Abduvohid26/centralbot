from datetime import datetime
import pytz
from environs import Env
import os
from dotenv import load_dotenv
load_dotenv()
api_url = "http://localhost:8000/upload-link"
env = Env()
env.read_env()
BOT_TOKEN = env.str("BOT_TOKEN")
OWNER_ID = env.int("OWNER_ID")

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

print("DB_USER:", DB_USER)
print("DB_PASS:", DB_PASS)
print("DB_HOST:", DB_HOST)
print("DB_NAME:", DB_NAME)
BASE_TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

BASE_API_URL = "http://127.0.0.1:8000"
CHECK_MEDIA_URL = f"{BASE_API_URL}/api/check-media/"  # <- to‘g‘ri nomlash
userbot_queues = {}
user_links = {}
ALLOWED_BOTS_API_URL = "http://84.32.188.155:8080/all/bot/username"
# ALLOWED_BOTS_API_URL = "https://a845c746fb09.ngrok-free.app/all/bot/username"
def toshkent_now() -> datetime:
    return datetime.now(pytz.timezone("Asia/Tashkent")).replace(tzinfo=None)


months_uz = {
    1: "yanvar", 2: "fevral", 3: "mart", 4: "aprel",
    5: "may", 6: "iyun", 7: "iyul", 8: "avgust",
    9: "sentabr", 10: "oktabr", 11: "noyabr", 12: "dekabr"
}

