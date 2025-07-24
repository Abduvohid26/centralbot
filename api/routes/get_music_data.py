

from telethon import TelegramClient, events
import asyncio
from telethon.sessions import StringSession
import random
api_id = 22209167
api_hash = "77603dcd30196b60487d2a6f7acb4702"
usernames = ['tarjimontgbot', '@Quronallbot', '@Mediabaza04bot', '@Mediabaza05bot', '@Mediabaza09bot', '@Mediabaza10bot', '@Mediabaza10bot', '@Mediabaza14bot']
bot_username = random.choice(usernames)

from bot.utils.database.functions.f_userbot import get_random_active_userbot

from telethon import TelegramClient, events
import os

import httpx


async def send_audio_to_chat(file_path: str, chat_id: int, bot_token: str, caption: str = "") -> dict | None:
    url = f"https://api.telegram.org/bot{bot_token}/sendAudio"
    timeout = httpx.Timeout(10.0)  # ⏰ 10 soniyadan oshmasligi shart

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
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

    except httpx.HTTPError as e:
        print(f"❌ HTTP xatolik: {e}")
    except Exception as e:
        print(f"❌ Umumiy xatolik: {e}")

    return None  # 🎯 Timeout yoki xatolik bo‘lsa None qaytadi
async def get_music_data(prompt: str, bot_token: str, chat_id: int, timeout: int = 12) -> dict | None:
    userbot = await get_random_active_userbot()

    client = TelegramClient(
        StringSession(userbot.session_string),
        userbot.app.api_id,
        userbot.app.api_hash
    )

    file_id = None
    message_id = None
    file_name = None
    audio_path = None
    audio_ready = asyncio.Event()

    async def cleanup():
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
                print("🧹 Fayl tozalandi.")
            except Exception as e:
                print(f"⚠️ Faylni o‘chirishda xatolik: {e}")
        if client.is_connected():
            await client.disconnect()
            print("🔌 Client uzildi.")

    @client.on(events.NewMessage(from_users=bot_username))
    async def handle_buttons(event):
        nonlocal file_name
        if event.buttons:
            for row in event.buttons:
                for button in row:
                    text = button.text.strip()
                    if "•" in text or ":" in text:
                        file_name = text
                        print(f"🎵 Tugma: {file_name}")
                        await event.click(text=text)
                        print("🔘 Tugma bosildi")
                        return

    @client.on(events.NewMessage(from_users=bot_username))
    async def handle_audio(event):
        nonlocal file_id, message_id, audio_path, file_name
        file = event.audio or event.document
        if not file:
            return

        print("🎧 Audio kelmoqda...")

        if file.size < 100 * 1024:
            print("⚠️ Juda kichik fayl (demo?) — bekor qilindi.")
            await cleanup()
            audio_ready.set()
            return

        try:
            safe_name = (file_name or f"audio_{chat_id}").replace(" ", "_") + ".mp3"
            audio_path = os.path.join("/tmp", safe_name)

            await client.download_media(file, audio_path)
            print(f"💾 Yuklandi: {audio_path}")

            result = await send_audio_to_chat(audio_path, chat_id, bot_token, caption=prompt)
            if result is None:
                print("❌ Audio yuborishda xatolik timeout")
                await cleanup()
                audio_ready.set()
                return
            file_id = result['file_id']
            message_id = result['message_id']
            print("✅ Telegramga yuborildi")

        except Exception as e:
            print(f"❌ Audio yuborishda xatolik: {e}")
        finally:
            audio_ready.set()
            await cleanup()

    try:
        await client.start()
        print("🚀 Userbot ishga tushdi")
        await client.send_message(bot_username, prompt)
        print(f"📩 '{prompt}' yuborildi")

        await asyncio.wait_for(audio_ready.wait(), timeout=timeout)

    except asyncio.TimeoutError:
        print(f"⏰ {timeout}s ichida audio kelmadi")
        await cleanup()
    except Exception as e:
        print(f"❌ Umumiy xatolik: {e}")
        await cleanup()

    # Doim yakunida None yoki dict qaytariladi
    if file_id and message_id and file_name:
        return {
            "file_id": file_id,
            "message_id": message_id,
            "file_name": file_name
        }
    else:
        return None