from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import Message
from bot.filters.platform_get import extract_platform_from_link
from bot.services.media_service import user_links
from bot.utils.database.functions.f_media import create_media
from bot.utils.database.functions.f_user import get_user_by_user_id, create_user

router = Router()

async def send_central_bot(link: str) -> str:
    return link

@router.message(Command("start"))
async def start_handler(message: types.Message):
    tg_user = message.from_user
    # 1️⃣ Avvalo foydalanuvchiga xabar yuboramiz
    await message.answer(
        "Assalomu alaykum!\n"
        "Link yuboring va faylni oling."
    )
    # 2️⃣ Bazada bormi-yo‘qligini tekshiramiz
    existing = await get_user_by_user_id(tg_user.id)
    if existing:
        return  # agar mavjud bo‘lsa, hech narsa qilmaymiz

    try:
        await create_user(
            user_id=tg_user.id,
            fullname=tg_user.full_name,
            username=tg_user.username,
            phone=None,  # agar telefon kerak bo‘lsa, boshqa yo‘l bilan oling
            language=tg_user.language_code,
            is_blocked=False,
            is_premium=False,
            is_admin=False,
            referral_id=None
        )
    except Exception as e:
        # Saqlashda xatolik bo‘lsa, loglash yoki foydalanuvchiga xabar
        await message.answer("❌ Ro‘yxatdan o‘tishda xatolik yuz berdi.")
        # (ixtiyoriy) logger.error(f"User create error: {e}")

@router.message(F.forward_from)
async def check_forwarded_media(message: Message):
    caption = message.caption
    if not caption:
        await message.answer("❗️Caption yo‘q.")
        return

    expected_link = user_links.get("filter_link")
    if not expected_link:
        await message.answer("❗️Mos link topilmadi.")
        return

    if expected_link in caption:
        file_id = None
        if message.video:
            file_id = message.video.file_id
        elif message.document:
            file_id = message.document.file_id
        elif message.photo:
            file_id = message.photo[-1].file_id

        if not file_id:
            await message.answer("❗️Fayl aniqlanmadi.")
            return

        # ✅ Platformani avtomatik ajratish
        platform = await extract_platform_from_link(expected_link)

        try:
            await create_media(
                platform=platform,
                link=expected_link,
                file_id=file_id,
                caption=caption,
                bot_username=None,
                bot_token=None,
                channel_message_id=None,
                channel_id=None,
            )
            await message.answer(f"✅ Media '{platform}' platformasi uchun saqlandi.")
        except Exception as e:
            print(f"❌ Xatolik: {e}")
            await message.answer("❌ Bazaga saqlashda xatolik yuz berdi.")
    else:
        await message.answer("❌ Captiondagi link mos kelmadi.")