import asyncio
from aiogram import Bot
from aiogram.enums import ParseMode
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.messages import ForwardMessagesRequest

BOT_TOKEN = "7676105696:AAGJgc2hgU9KQ6VjvsxxjHAWoJMbNbdFjCY"
USER_TELEGRAM_ID = 6629227976
VIDEO_FILE_ID = "BAACAgIAAxkBAAIEGGhVHR-NTXMVDfuANZ-cCCNHdqW7AAIzcgACEkxpST70ME8669UVNgQ"
CAPTION_LINK = "https://www.instagram.com/reels/DI4CZ-voPEl/"

api_id = 13335511
api_hash = "c78601a9248b8f76b631368cb14c44ff"
userbot_session = "1ApWapzMBu3SN5lONZOlH8-9lnFJahULHOba1OOXFWlK-iba0BBxY9C82s-VDathIyLB0g1eoSju0Bo8cNiF4lP6rU9XZdAXV0KARxmgQjdJRag89YGwMVMffeGowqPVJe1ldfcNC7xM5VfLm7GsB7rtLamptX7w4GHIvUVHcEYWcx5ubtPp09vCo9CCD8j6iyIZPCASlc3zifymTdK9r7uisG7wEF_tkn3PetkWomBoq0-B6eQbkojFaj16WOwTSEK_XRvyQE1fIlgH23ZJKq61CL_F3JnGhK_X70ZqaljW31CLemtbXpBmL_GdsRbVdMFVEX_QG_82A-Bz0J0TbSUcr_N79g3M="  # <-- to‘liq session bo'lishi kerak
FORWARD_TO_ID = 6629227976

message_id_holder = {"target_message_id": None}

async def send_video_with_bot():
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    print("📤 A bot — userbotga video yuborilmoqda...")

    await bot.send_video(
        chat_id=USER_TELEGRAM_ID,
        video=VIDEO_FILE_ID,
        caption=CAPTION_LINK
    )

    await bot.session.close()

async def run_userbot():
    client = TelegramClient(StringSession(userbot_session), api_id, api_hash)
    @client.on(events.NewMessage())
    async def handler(event):
        # target_id = message_id_holder["target_message_id"]
        message_text = event.message.message
        print("caption link: ", CAPTION_LINK)
        if message_text and CAPTION_LINK in message_text:
            print("🎯 Mos keladigan xabar topildi!")
            print(event.chat_id)
            try:
                await client(ForwardMessagesRequest(
                    from_peer=event.chat_id,
                    to_peer="@chatuz_1bot",
                    id=[event.message.id],
                    with_my_score=False
                ))
                print("📤 Xabar B botga forward qilindi!")
            except Exception as e:
                print("❌ Forwardda xatolik:", e)
        else:
            print(f"⏺️ Kutilmagan xabar ID: {event.message.id}")

    await client.start()
    print("👀 Userbot xabarni kutmoqda...")
    await client.run_until_disconnected()

async def main():
    userbot_task = asyncio.create_task(run_userbot())

    await asyncio.sleep(3)

    await send_video_with_bot()

    await userbot_task

if __name__ == "__main__":
    asyncio.run(main())
