# from telethon import TelegramClient, events
# from telethon.sessions import StringSession
# import os
#
# bot_username = "@testchibotbot"
# CHANNEL = -1002241939017  # Kanal ID
#
# async def forward_to_other_bot(userbot, to_bot):
#     client = TelegramClient(
#         StringSession(userbot.session_string),
#         userbot.app.api_id,
#         userbot.app.api_hash
#     )
#     print("✅ Userbot ishga tushdi. Kutilmoqda...")
#
#     @client.on(events.NewMessage(chats=bot_username))
#     async def handle_message(event):
#         msg = event.message
#         print("\n📩 Yangi xabar keldi!")
#
#         if msg.media:
#             file_path = await client.download_media(msg)
#             print("✅ Yuklab olindi:", file_path)
#
#             # 🔁 O‘sha botga qayta yuborish
#             await client.send_file(to_bot, file_path, caption=msg.text or "")
#             print("📤 Botga yuborildi")
#
#             os.remove(file_path)
#
#         else:
#             await client.send_message(to_bot, msg.text or "[Matn yo‘q]")
#             print("📤 Matn botga yuborildi")
#
#     await client.run_until_disconnected()
#
