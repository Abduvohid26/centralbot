from telethon import TelegramClient, events
from telethon.sessions import StringSession
import os

bot_username = "@testchibotbot"
CHANNEL = -1002241939017  # Kanal ID

async def forward_to_other_bot(userbot):
    client = TelegramClient(
        StringSession(userbot.session_string),
        userbot.app.api_id,
        userbot.app.api_hash
    )

    await client.start()
    print("✅ Userbot ishga tushdi. Kutilmoqda...")

    @client.on(events.NewMessage(chats=bot_username))
    async def handle_message(event):
        msg = event.message
        print("\n📩 Yangi xabar keldi!")

        if msg.text:
            print("📝 Matn:", msg.text)

        if msg.media:
            try:
                print("📥 Media aniqlangan. Yuklab olinmoqda...")
                file_path = await client.download_media(msg)
                print("✅ Fayl yuklab olindi:", file_path)

                await client.send_file(CHANNEL, file_path, caption=msg.text or "")
                print(f"📤 Kanalga yuborildi: {CHANNEL}")

                os.remove(file_path)
                print("🧹 Fayl o‘chirildi:", file_path)

            except Exception as e:
                print("❌ Xatolik media yuborishda:", e)

        else:
            print("❌ Bu xabarda media yo‘q. Matn kanalga yuboriladi.")
            await client.send_message(CHANNEL, msg.text or "[Matn yo‘q]")
            print("📤 Matn kanalga yuborildi.")

    await client.run_until_disconnected()
