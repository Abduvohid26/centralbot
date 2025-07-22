from aiogram import Router, F, Dispatcher
from aiogram.types import Message

def register_media_handler(dp: Dispatcher, expected_link: str, clent_id: int):
    router = Router()
    @router.message(F.video)
    async def save_video_handler(message: Message):
        incoming_caption = (message.caption or "").strip()
        if incoming_caption != expected_link:
            return

        await message.answer("✅ Video va link va file_id bazaga saqlandi.")
        print("clentga yubordiiiii")
        file_id = message.video.file_id
        await message.bot.send_video(chat_id=clent_id, video=file_id)

        # Polling’ni to‘xtatish
        await message.answer("✅ Bot ishlashini tugatdi!")
        await message.bot.session.close()
        await dp.stop_polling()  # eng to‘g‘ri usul

    dp.include_router(router)

