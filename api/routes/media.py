import aiohttp
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from fastapi import APIRouter, HTTPException
from telethon import TelegramClient
from telethon.sessions import StringSession
from api.schemas.media import MediaRequest, ExternalOnlyRequest, BotUsername, AudioTextRequest
from bot.data.config import ALLOWED_BOTS_API_URL, userbot_queues
from bot.filters.platform_get import extract_platform_from_link
from bot.loader import bot
from bot.utils.database.functions.f_dbbot import get_random_bot_username
from bot.utils.database.functions.f_media import get_media_by_link
from bot.utils.database.functions.f_stat_link import detect_social_network, increment_social_network_stat
from bot.utils.database.functions.f_userbot import  get_all_user_bots, get_random_active_userbot
# MEDIA_BAZA = ["Mediabaza13bot", "Mediabaza14bot", "Mediabaza10bot", "Mediabaza09bot", "Mediabaza05bot", "Mediabaza04bot", "Quronallbot", "tarjimontgbot"]
MEDIA_BAZA = ["ilxa26_bot", "Abduvohid25_bot"]
router = APIRouter()

async def analyze_and_increment(link: str):
    network = detect_social_network(link)
    await increment_social_network_stat(network)

@router.post("/check-media")
async def check_media(data: MediaRequest):
    platform = await extract_platform_from_link(data.external_link)
    queue = userbot_queues.get(int(data.userbot_id))
    if platform == 'youtube':
        media = await get_media_by_link(platform)
    else:
        media = await get_media_by_link(data.external_link)
    await analyze_and_increment(data.external_link)
    is_media = media is not None
    if not queue:
        raise HTTPException(status_code=404, detail="UserBot mavjud emas yoki hali ishga tushmagan")
    await queue.put({
        "external_link": data.external_link,
        "external_bot_username": data.external_bot_username,
        "is_media": is_media
    })
    print({"status": True, "message": "UserBot o'z ishini bajarishga tushdi✅"})
    return {"status": True, "message": "UserBot o'z ishini bajarishga tushdi✅"}

@router.post("/send-external-media")
async def external_media(data: ExternalOnlyRequest):
    print("Salom")
    # platform = await extract_platform_from_link(data.link)
    media = await get_media_by_link(data.external_link)
    if not media:
        print("121221")
        return {"status": False}
    await analyze_and_increment(data.external_link)
    file_id = media.file_id
    is_media = media is not None
    userbot = await get_random_active_userbot()
    queue = userbot_queues.get(userbot.telegram_user_id)
    if not queue:
        print("hi")
        raise HTTPException(status_code=404, detail="UserBot mavjud emas yoki hali ishga tushmagan")
    await queue.put({
        "external_link": data.external_link,
        "external_bot_username": data.external_bot_username,
        "is_media": is_media
    })
    # 1️⃣ Avval asosan ishlatiladigan bot orqali yuborishga harakat qilamiz
    print("malumotlar>>", userbot.phone_number, "   ", file_id)
    try:
        await bot.send_video(
            chat_id=userbot.telegram_user_id,
            video=file_id,
            caption=f"{data.external_link} media26",
        )
        return {"status": True, "message": f"✅ Video yuborildi"}

    # 2️⃣ Agar bu botga tegishli bo‘lmasa, asl bot_token orqali yuboramiz
    except TelegramAPIError as e:
        print(f"❌ Asosiy bot orqali yuborilmadi: {e}")
        try:
            # Asl botni yaratamiz
            temp_bot = Bot(token=media.bot_token)
            await temp_bot.send_video(
                chat_id=userbot.telegram_user_id,
                video=file_id,
                caption=f"{data.external_link} media26",
            )
            await temp_bot.session.close()
            return {"status": True, "message": "✅ Asl bot orqali video yuborildi (fallback)"}
        except Exception as second_error:
            print(f"❌ Fallback bot bilan ham yuborib bo‘lmadi: {second_error}")
            return {"status": False, "error": str(second_error)}

@router.get("/random-userbot")
async def get_random_active_userbots():
    userbot = await get_random_active_userbot()
    if not userbot or not userbot.app:
        raise HTTPException(status_code=404, detail="No active userbots found.")
    return {
        "telegram_user_id": userbot.telegram_user_id,
        "api_id": userbot.app.api_id,
        "api_hash": userbot.app.api_hash
    }

async def fetch_allowed_usernames() -> list[str]:
    return MEDIA_BAZA
    # async with aiohttp.ClientSession() as session:
    #     async with session.get(ALLOWED_BOTS_API_URL) as resp:
    #         if resp.status == 200:
    #             data = await resp.json()
    #             return [
    #                 item["username"].lstrip("@")
    #                 for item in data.get("data", [])
    #                 if "username" in item
    #             ] + MEDIA_BAZA
    #         return []

@router.post("/send-new-bot-username")
async def add_allowed_bot(data: BotUsername):
    userbots = await get_all_user_bots()
    bot_username = data.bot_username

    if not bot_username:
        return {"status": "error", "message": "Bot username bo‘sh bo‘lishi mumkin emas"}

    success_count = 0
    fail_count = 0

    for userbot in userbots:
        try:
            print(f"🚀 {userbot.phone_number} → userbot ishga tushmoqda...")
            client = TelegramClient(
                StringSession(userbot.session_string),
                userbot.app.api_id,
                userbot.app.api_hash
            )
            await client.start()
            try:
                await client.send_message(bot_username, "/start")
                print(f"✅ {userbot.phone_number} → /start yuborildi → @{bot_username}")
                success_count += 1
            except Exception as send_err:
                print(f"❌ {userbot.phone_number} → Xatolik @{bot_username} ga yuborishda: {send_err}")
                fail_count += 1
            await client.disconnect()
        except Exception as userbot_err:
            print(f"❌ {userbot.phone_number} → Xatolik: {userbot_err}")
            fail_count += 1

    return {
        "status": "success",
        "message": f"/start komandasi yuborildi → @{bot_username}",
        "details": {
            "success": success_count,
            "failed": fail_count,
            "total": len(userbots)
        }
    }

@router.post("/receive-audio-text")
async def receive_audio_text(data: AudioTextRequest):
    try:
        # 1. Bazadan random aktiv userbot olish
        userbot = await get_random_active_userbot()
        if not userbot:
            raise HTTPException(status_code=404, detail="Faol userbot topilmadi ❌")

        # 2. Shu userbot uchun queue olish
        queue = userbot_queues.get(userbot.telegram_user_id)
        if not queue:
            raise HTTPException(status_code=404, detail="UserBot ishga tushmagan yoki queue yo'q ❌")

        # 3. UserBot navbatiga topshiriq berish
        db_username = await get_random_bot_username()
        if not db_username:
            return {"status": False}
        await queue.put({
            "type": "send_audio_text",
            "audio_text": data.audio_text,
            "external_bot_username": data.external_bot_username,
            "db_username": db_username
        })

        return {
            "status": True,
            "message": f"✅ Audio text '{data.audio_text[:10]}...' userbotga topshirildi.",
            "userbot_id": userbot.telegram_user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ichki xatolik: {e}")


from api.routes.get_music_data import get_music_data

@router.get("/find-music")
async def muz_router(prompt: str, bot_token: str, chat_id: int):
    try:
        file_id = await get_music_data(prompt, bot_token, chat_id)  # 🔁 Endi file_id olish mumkin
        if file_id is not None:
            return {
                "message": f"🎵 '{prompt}' yuborildi!",
                "success": True,
                "data": file_id
            }
        else:
            return {
                "message": f"🎵 '{prompt}' yuborilmadi!",
                "success": False
            }
    except Exception as e:
        return {
            "message": f"Xatolik ({prompt}): {e}",
            "success": False
        }
# from telethon import events
# import asyncio


# async def start_audio_forwarding(track_id: str, target_bot_username: str):
#     media = await get_media_by_link(track_id)
#     if not media:
#         return {"success": False, "message": "Media topilmadi"}

#     userbot = await get_random_active_userbot()
#     if not userbot:
#         return {"success": False, "message": "Userbot topilmadi"}

#     client = TelegramClient(
#         StringSession(userbot.session_string),
#         userbot.app.api_id,
#         userbot.app.api_hash
#     )

#     # 📌 Future yaratamiz natijani kutish uchun
#     result_future = asyncio.Future()

#     @client.on(events.NewMessage(incoming=True))
#     async def handle_audio(event):
#         if event.message.audio and "media26" in (event.message.message or "") and target_bot_username in event.message.message:
#             try:
#                 await client.send_file(
#                     entity=f"@{target_bot_username}",
#                     file=event.message.audio,
#                     caption="✅ Userbot orqali yuborildi"
#                 )
#                 if not result_future.done():
#                     result_future.set_result({"success": True, "message": "Userbot orqali yuborildi"})
#             except Exception as e:
#                 if not result_future.done():
#                     result_future.set_result({"success": False, "message": f"Yuborishda xatolik: {e}"})

#     await client.start()

#     # Main bot orqali userbotga yuborish
#     try:
#         tempbot = Bot(token=media.bot_token)
#         await tempbot.send_audio(
#             chat_id=userbot.telegram_user_id,
#             audio=media.file_id,
#             caption=f"{media.link} media26 {target_bot_username}"
#         )
#     except Exception as e:
#         await client.disconnect()
#         return {"success": False, "message": f"Bot yuborishda xatolik: {e}"}

#     # Userbotdan natijani kutish
#     try:
#         result = await asyncio.wait_for(result_future, timeout=5)
#     except asyncio.TimeoutError:
#         result = {"success": False, "message": "⏱ Userbotdan javob kelmadi (timeout)"}
#     finally:
#         await client.disconnect()

#     return result


@router.get("/new-api-send")
async def new_api_send(track_id: str, bot_username: str):
    return await send_to_external_bot_via_userbot(track_id, bot_username)



from telethon import TelegramClient
from telethon.sessions import StringSession
from aiogram import Bot
import aiohttp
from io import BytesIO

# Asosiy endpoint
@router.get("/new-api-send")
async def new_api_send(track_id: str, bot_username: str):
    return await send_to_external_bot_via_userbot(track_id, bot_username)

# Asosiy funksiya
async def send_to_external_bot_via_userbot(track_id, bot_username):
    # 1. DB dan media olish
    media = await get_media_by_link(track_id)
    if not media:
        return {"success": False, "message": "Media not found"}

    # 2. Faol userbot olish
    userbot = await get_random_active_userbot()
    if not userbot:
        return {"success": False, "message": "Userbot not found"}

    # 3. Telethon client yaratish
    client = TelegramClient(
        StringSession(userbot.session_string),
        userbot.app.api_id,
        userbot.app.api_hash
    )

    await client.start()

    # 4. Audio faylni URL orqali olish
    base_bot = Bot(token=media.bot_token)
    async with base_bot:
        file = await base_bot.get_file(media.file_id)
        file_path = file.file_path
        file_url = f"https://api.telegram.org/file/bot{media.bot_token}/{file_path}"

    # 5. Faylni yuklab olish va RAMga yozish (diskga emas!)
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as resp:
            if resp.status != 200:
                await client.disconnect()
                return {"success": False, "message": "File download failed"}
            audio_bytes = await resp.read()

    # 6. BytesIO (xotirada fayl obyekti)
    file_obj = BytesIO(audio_bytes)
    file_obj.name = "audio.mp3"  # Fayl nomi berilishi kerak

    # 7. Userbot orqali tashqi botga yuborish
    try:
        await client.send_file(
            entity=f"@{bot_username}",
            file=file_obj,
            caption="✅ Userbot orqali yuborildi"
        )
        print("✅ Audio yuborildi userbot orqali")
        return {"success": True, "message": "Audio yuborildi"}
    except Exception as e:
        print("❌ Yuborishda xatolik:", e)
        return {"success": False, "message": str(e)}
    finally:
        await client.disconnect()