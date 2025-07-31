

from telethon import TelegramClient, events
import asyncio
from telethon.sessions import StringSession
import random
from telethon.tl.functions.channels import JoinChannelRequest

api_id = 22209167
api_hash = "77603dcd30196b60487d2a6f7acb4702"
usernames = ['tarjimontgbot', '@Quronallbot', '@Mediabaza04bot', '@Mediabaza05bot', '@Mediabaza09bot', '@Mediabaza10bot', '@Mediabaza10bot', '@Mediabaza14bot']
# bot_username = random.choice(usernames)
bot_username = 'AudioSavedBot'
from bot.utils.database.functions.f_userbot import get_random_active_userbot, get_random_active_userbot_exta

from telethon import TelegramClient, events
import os

import httpx
TEMP_DIR = "/tmp"


async def send_audio_to_chat(file_path: str, chat_id: int, bot_token: str, caption: str = "") -> dict | None:
    url = f"https://api.telegram.org/bot{bot_token}/sendAudio"
    timeout = httpx.Timeout(connect=5.0, read=30.0, write=30.0, pool=5.0)

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

    except Exception as e:
        print(f"❌ Audio yuborishda xatolik: {e}")
    return None

# 🎯 Asosiy funksiya

async def get_music_data(prompt: str, bot_token: str, chat_id: int, timeout: int = 30) -> dict | None:
    userbot = await get_random_active_userbot_exta()

    client = TelegramClient(
        StringSession(userbot.session_string),
        userbot.app.api_id,
        userbot.app.api_hash
    )

    audio_ready = asyncio.Event()
    response_event = asyncio.Event()
    latest_event = None
    audio_path = None
    file_id = None
    message_id = None
    file_name = f"audio_{chat_id}.mp3"

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

    async def join_channel(channel_url: str):
        username = channel_url.split("https://t.me/")[-1]
        try:
            await client(JoinChannelRequest(username))
            print(f"✅ Kanalga qo‘shildi: {username}")
        except Exception as e:
            print(f"❌ Kanalga qo‘shishda xatolik: {e}")

    @client.on(events.NewMessage(from_users=bot_username))
    async def unified_handler(event):
        nonlocal latest_event, audio_path, file_id, message_id


        if event.audio or event.document:
            file = event.audio or event.document
            if file.size < 100 * 1024:
                print("⚠️ Demo fayl – e'tiborsiz")
                return

            try:
                audio_path = os.path.join(TEMP_DIR, file_name)
                await client.download_media(file, audio_path)
                print(f"💾 Yuklandi: {audio_path}")

                result = await send_audio_to_chat(audio_path, chat_id, bot_token, caption=prompt)
                if result:
                    file_id = result['file_id']
                    message_id = result['message_id']
                    print("✅ Telegramga yuborildi")
                    audio_ready.set()
            except Exception as e:
                print(f"❌ Audio yuklashda xatolik: {e}")
                audio_ready.set()

        if event.buttons:
            first_button = event.buttons[0][0]

            # ➕ Obuna bo‘lish tugmasi bo‘lsa
            if "obuna" in first_button.text.lower():
                if hasattr(first_button, "url") and first_button.url:
                    await join_channel(first_button.url)

                # ✅ Obuna bo‘lingach, tugmani qayta bosamiz
                await client.send_message(bot_username, prompt)
                try:
                    await event.click(text=first_button.text)
                except Exception as e:
                    print(f"❌ Tugma qayta bosishda xatolik: {e}")

            else:
                # Birinchi tugmani bosamiz (agar obuna bo‘lish bo‘lmasa)
                try:
                    await event.click(text=first_button.text)
                except Exception as e:
                    print(f"❌ Tugma bosishda xatolik: {e}")


    try:
        await client.start()
        print("🚀 Userbot ishga tushdi")

        await client.send_message(bot_username, prompt)
        print(f"📩 Prompt yuborildi: {prompt}")

        # 5s ichida tugmalar keladi deb kutamiz
        try:
            await asyncio.wait_for(response_event.wait(), timeout=5)
            if latest_event and latest_event.buttons:
                for row in latest_event.buttons:
                    for btn in row:
                        if hasattr(btn, "url") and btn.url:
                            await join_channel(btn.url)
        except asyncio.TimeoutError:
            print("⏱️ Tugmalar javobi kelmadi")

        await asyncio.wait_for(audio_ready.wait(), timeout=timeout)

    except asyncio.TimeoutError:
        print(f"⏰ {timeout}s ichida audio kelmadi")
    except Exception as e:
        print(f"❌ Umumiy xatolik: {e}")
    finally:
        await cleanup()

    return {
        "file_id": file_id,
        "message_id": message_id,
        "file_name": file_name
    } if file_id and message_id and file_name else None