import asyncio
import uvicorn
import os
from dotenv import load_dotenv
from bot.services.media_service import start_all_userbots
from bot.telethon_utils.send_start import send_start_to_all_allowed_bots

# ✅ .env faylni konteyner ichida yuklash
load_dotenv(dotenv_path="/app/.env")

from bot.utils.database.functions.f_media import import_media_from_csv
from bot.app import run_bot
from api.main import app as fastapi_app

async def run_api():
    config = uvicorn.Config(fastapi_app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    await asyncio.gather(
        run_bot(),
        run_api(),
        send_start_to_all_allowed_bots(),
        start_all_userbots()
    )
    if os.getenv("IMPORT_CSV", "false").lower() == "true":
        print("📥 CSV fayldan ma’lumotlar import qilinmoqda...", flush=True)
        await import_media_from_csv("/app/redis_tiktok.csv")
        print("✅ CSV dan import tugadi", flush=True)
        return

if __name__ == "__main__":
    asyncio.run(main())
