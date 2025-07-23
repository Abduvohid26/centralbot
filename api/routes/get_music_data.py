

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
            files = {'audio': (file_path, audio_file)}
            data = {'chat_id': chat_id, 'caption': caption}
            response = await client.post(url, data=data, files=files)
            response.raise_for_status()
            result = response.json()
            print(result, "✅ Telegram javobi")
            file_id = result['result']['audio']['file_id']
            message_id = result['result']['message_id']
            return {
                "file_id": file_id,
                "message_id": message_id
            }
from bot.utils.database.functions.f_userbot import  get_random_active_userbot
from telethon.sessions import StringSession
import asyncio

async def get_music_data(prompt: str, bot_token: str, chat_id: int) -> dict | None:

    userbot = await get_random_active_userbot()
    
    client = TelegramClient(
        StringSession(userbot.session_string),
        userbot.app.api_id, userbot.app.api_hash
        )

    audio_received = False
    button_clicked = False
    file_id = None
    message_id = None
    file_name = None

    @client.on(events.NewMessage(from_users=bot_username))
    async def handle_buttons(event):
        nonlocal button_clicked, file_name
        if button_clicked:
            return

        if event.buttons:
            for row in event.buttons:
                for button in row:
                    if "•" in button.text or ":" in button.text:
                        file_name = button.text.strip() 
                        print(f"🎵 Tugma topildi: {file_name}")
                        await event.click(text=button.text)
                        print("🔘 Tugma bosildi")
                        button_clicked = True
                        return

    @client.on(events.NewMessage(from_users=bot_username))
    async def handle_audio(event):
        await asyncio.sleep(1)
        nonlocal audio_received, file_id, message_id
        if audio_received:
            return

        if event.audio or event.document:
            audio_received = True
            file = event.audio or event.document
            print("🎧 Audio topildi, yuklanmoqda...")

            try:
                file_path = f"{file_name.split('•')[-1]}" + ".mp3"
                await client.download_media(file, file_path)
                print(f"💾 Yuklandi: {file_path}")

                # Telegramga yuboramiz
                result = await send_audio_to_chat(
                    file_path=file_path,
                    chat_id=chat_id,
                    bot_token=bot_token,
                    caption=prompt
                )

                file_id = result["file_id"]
                message_id = result["message_id"]

                print(f"📤 Yuborildi. file_id: {file_id}")
                os.remove(file_path)
                print("🧹 Fayl o‘chirildi.")
            except Exception as e:
                print(f"❌ Xatolik: {e}")
            finally:
                await client.disconnect()

    await client.start()
    print("🚀 Client ishga tushdi")
    await client.send_message(bot_username, prompt)
    print(f"📩 '{prompt}' botga yuborildi")
    await client.run_until_disconnected()

    if file_id and message_id and file_name:
        return {
            "file_id": file_id,
            "message_id": message_id,
            "file_name": file_name
        }
    return None
