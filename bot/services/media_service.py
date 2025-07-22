import asyncio
from telethon import TelegramClient, events, functions
from telethon.sessions import StringSession
from telethon.tl.functions.messages import ForwardMessagesRequest
from api.routes.media import fetch_allowed_usernames
from bot.data.config import user_links, userbot_queues
from bot.loader import bot
from bot.utils.database.functions.f_userbot import get_all_user_bots

async def run_userbot(userbot):
    client = TelegramClient(
        StringSession(userbot.session_string),
        userbot.app.api_id,
        userbot.app.api_hash
    )
    queue = asyncio.Queue()
    userbot_queues[userbot.telegram_user_id] = queue
    print("shu userbotishladi>>>", userbot.telegram_user_id)
    rules = []
    allowed_bot_ids = []
    print('7777777>>', userbot.id)
    print(f"📦 Queue qo‘shildi: userbot_id={userbot.id}, queue={queue}")
    print(f"📋 Hozirgi userbot_queues: {userbot_queues}")
    # ✅ Dastlab ruxsat etilgan botlar ID sini olish
    async def resolve_allowed_bot_ids():
        ALLOWED_BOT_USERNAMES = await fetch_allowed_usernames()
        print("shularni kuzatadi>>> ", ALLOWED_BOT_USERNAMES)
        for username in ALLOWED_BOT_USERNAMES:
            try:
                entity = await client.get_entity(username)
                allowed_bot_ids.append(entity.id)
                print(f"✅ Bot {username} → ID: {entity.id}")
            except Exception as inner_e:
                print(f"❌ {username} ni aniqlab bo'lmadi: {inner_e}")

    # 📥 Queue orqali qabul qilingan forward qoidalarni kuzatish
    async def listen_for_rules():
        while True:
            rule = await queue.get()
            print("🆕 Yangi rule qabul qilindi:", rule)
            rules.append(rule)
    # 📩 Yangi xabar kelganini kuzatish
    @client.on(events.NewMessage(incoming=True, from_users=allowed_bot_ids))
    async def handler(event):
        sender_id = event.message.sender_id

        if sender_id not in allowed_bot_ids:
            return  # ❌ Ruxsat etilmagan jo'natuvchi

        message_text = getattr(event.message, "message", "")
        print("📨 Xabar (ruxsat etilgan botdan):", message_text)

        if event.message.media and message_text:
            print("🆕 Yangi media bilan caption:", message_text)

        for rule in rules:
            if rule["external_link"] in message_text:
                print("🎯 Mos keladigan xabar topildi!")
                try:
                    from_peer = await client.get_input_entity(event.chat_id)

                    # 📦 Avval external_bot_username ga forward qilamiz
                    to_peer = await client.get_input_entity(rule["external_bot_username"])
                    await client(ForwardMessagesRequest(
                        from_peer=from_peer,
                        to_peer=to_peer,
                        id=[event.message.id],
                        with_my_score=False
                    ))
                    print(f"✅ Forward qilindi → {rule['external_bot_username']}")

                    # 🔁 Agar media yo'q bo'lsa, markaziy botga ham forward qilamiz
                    if rule.get("is_media") is False:
                        user_links["filter_link"] = rule["external_link"]
                        me = await bot.get_me()
                        BOT_USERNAME = me.username
                        print("Markaziy_bot username>>>", BOT_USERNAME)
                        try:
                            markaziy_peer = await client.get_input_entity(BOT_USERNAME)
                            await client(ForwardMessagesRequest(
                                from_peer=from_peer,
                                to_peer=markaziy_peer,
                                id=[event.message.id],
                                with_my_score=False
                            ))
                            print(f"📩 Forward qilindi → {BOT_USERNAME}")
                        except Exception as one_e:
                            print(f"❌ Markaziy botga forwardda xatolik: {one_e}")
                    rules.remove(rule)
                except Exception as inner_e:
                    print("❌ Forward qilishda tashqi xatolik:", inner_e)

    try:
        await client.start()
        print(f"👀 Userbot ishga tushdi: {userbot.phone_number}")
    except Exception as e:
        print(f"❌ Userbotni start() qilishda xatolik: {e}")
        return
    await resolve_allowed_bot_ids()  # 🔥 Bot IDlarini olish
    asyncio.create_task(listen_for_rules())
    await client.run_until_disconnected()

# 🔁 Barcha userbotlarni ishga tushirish
async def start_all_userbots():
    userbots = await get_all_user_bots()
    print(f"🧠 Bazadan {len(userbots)} ta userbot olindi.")
    tasks = []
    for userbot in userbots:
        print(f"✅ Userbot ishga tushyapti: {userbot.phone_number} ({userbot.telegram_user_id})")
        try:
            task = asyncio.create_task(run_userbot(userbot))
            tasks.append(task)
        except Exception as e:
            print(f"❌ {userbot.phone_number} userbotni ishga tushirib bo‘lmadi: {e}")

    # Barcha userbot tasklari tugamaguncha kutadi
    await asyncio.gather(*tasks)


