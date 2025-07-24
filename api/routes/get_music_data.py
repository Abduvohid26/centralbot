

from telethon import TelegramClient, events
import asyncio
from telethon.sessions import StringSession
import random
api_id = 22209167
api_hash = "77603dcd30196b60487d2a6f7acb4702"
usernames = ['tarjimontgbot', '@Quronallbot', '@Mediabaza04bot', '@Mediabaza05bot', '@Mediabaza09bot', '@Mediabaza10bot', '@Mediabaza10bot', '@Mediabaza14bot']
bot_username = random.choice(usernames)


from telethon import TelegramClient, events
import os

import httpx

async def send_audio_to_chat(file_path: str, chat_id: int, bot_token: str, caption: str = "") -> dict:
    url = f"https://api.telegram.org/bot{bot_token}/sendAudio"
    async with httpx.AsyncClient() as client:
        with open(file_path, 'rb') as audio_file:
            files = {'audio': (os.path.basename(file_path), audio_file, 'audio/mpeg')}
            data = {'chat_id': chat_id, 'caption': caption}
            response = await client.post(url, data=data, files=files)
            response.raise_for_status()
            result = response.json()
            print(result, "✅ Telegram javobi")
            return {
                "file_id": result['result']['audio']['file_id'],
                "message_id": result['result']['message_id']
            }


async def get_music_data(prompt: str, bot_token: str, chat_id: int) -> dict | None:
    userbot = await get_random_active_userbot()

    client = TelegramClient(
        StringSession(userbot.session_string),
        userbot.app.api_id,
        userbot.app.api_hash
    )

    file_id = None
    message_id = None
    file_name = None
    audio_downloaded = asyncio.Event()
    audio_file_path = None

    async def cleanup():
        if audio_file_path and os.path.exists(audio_file_path):
            os.remove(audio_file_path)
            print("🧹 Fayl tozalandi.")
        await client.disconnect()
        print("🔌 Client uzildi.")

    @client.on(events.NewMessage(from_users=bot_username))
    async def handle_buttons(event):
        nonlocal file_name
        if event.buttons:
            for row in event.buttons:
                for button in row:
                    if "•" in button.text or ":" in button.text:
                        file_name = button.text.strip()
                        print(f"🎵 Tugma topildi: {file_name}")
                        await event.click(text=button.text)
                        print("🔘 Tugma bosildi")
                        return

    @client.on(events.NewMessage(from_users=bot_username))
    async def handle_audio(event):
        nonlocal file_id, message_id, file_name, audio_file_path
        if event.audio or event.document:
            file = event.audio or event.document
            print("🎧 Audio qabul qilindi, yuklanmoqda...")

            if file.size < 100 * 1024:
                print("⚠️ Fayl juda kichik, ehtimol demo. Bekor qilindi.")
                await cleanup()
                return

            if not file_name:
                file_name = f"track_{chat_id}.mp3"

            audio_file_path = os.path.join("/tmp", file_name.replace(" ", "_") + ".mp3")
            await client.download_media(file, audio_file_path)
            print(f"💾 Yuklandi: {audio_file_path}")

            try:
                result = await send_audio_to_chat(audio_file_path, chat_id, bot_token, caption=prompt)
                file_id = result["file_id"]
                message_id = result["message_id"]
                print(f"📤 Yuborildi. file_id: {file_id}")
            except Exception as e:
                print(f"❌ Yuborishda xatolik: {e}")
            finally:
                audio_downloaded.set()
                await cleanup()

    try:
        await client.start()
        print("🚀 Userbot ishga tushdi.")
        await client.send_message(bot_username, prompt)
        print(f"📩 '{prompt}' so‘rovi yuborildi")

        try:
            await asyncio.wait_for(audio_downloaded.wait(), timeout=60)  # max 60s kutish
        except asyncio.TimeoutError:
            print("⏰ Timeout! Audio kelmadi.")
            await cleanup()

    except Exception as e:
        print(f"❌ Umumiy xatolik: {e}")
        await cleanup()

    if file_id and message_id and file_name:
        return {
            "file_id": file_id,
            "message_id": message_id,
            "file_name": file_name
        }

    return None