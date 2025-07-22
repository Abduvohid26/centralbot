from aiogram import Router, F
from aiogram.types import Message
from bot.filters.platform_get import extract_platform_from_link
from bot.utils.database.functions.f_media import create_media, get_media_by_link

router = Router()

@router.message(F.video)
async def save_video_handler(message: Message):
    incoming_caption = (message.caption or "").strip()
    file_id = message.video.file_id
    media = await get_media_by_link(incoming_caption)

    if media:
        await message.answer("⚠️ Bu link allaqachon bazada mavjud.")
        return
    platform = await extract_platform_from_link(incoming_caption)
    await create_media(
        platform=platform,
        link=incoming_caption,
        file_id=file_id,
        caption=incoming_caption
    )
    await message.bot.session.close()
