import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from bot.utils.database.functions.f_userbot import get_all_user_bots
from api.routes.media import fetch_allowed_usernames  # bu API dan list[str] qaytaradi


async def send_start_to_all_allowed_bots():
    # 1. API dan allowed botlar ro‘yxatini olamiz
    allowed_bot_usernames = await fetch_allowed_usernames()
    if not allowed_bot_usernames:
        print("❌ Ruxsat etilgan botlar yo'q")
        return

    # 2. Bazadan barcha userbotlarni olamiz
    userbots = await get_all_user_bots()
    print(f"🧠 {len(userbots)} ta userbot olindi bazadan.")
    print(f"✅ {len(allowed_bot_usernames)} ta ruxsat etilgan bot: {allowed_bot_usernames}")

    # 3. Har bir userbot orqali /start yuboramiz
    for userbot in userbots:
        try:
            print(f"🚀 {userbot.phone_number} → userbot ishga tushmoqda...")
            client = TelegramClient(
                StringSession(userbot.session_string),
                userbot.app.api_id,
                userbot.app.api_hash
            )
            await client.start()

            for bot_username in allowed_bot_usernames:
                try:
                    await client.send_message(bot_username, "/start")
                    print(f"✅ {userbot.phone_number} → /start yuborildi → @{bot_username}")
                    await asyncio.sleep(1)
                except Exception as send_err:
                    print(f"❌ {userbot.phone_number} → Xatolik @{bot_username} ga yuborishda: {send_err}")

            await client.disconnect()
        except Exception as userbot_err:
            print(f"❌ {userbot.phone_number} → Xatolik: {userbot_err}")


# 🔁 Fayl mustaqil ishga tushirilganda
if __name__ == "__main__":
    asyncio.run(send_start_to_all_allowed_bots())
