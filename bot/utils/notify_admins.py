from aiogram import Bot
from aiogram.types import ReplyKeyboardRemove

async def on_startup_notify(bot: Bot):
    from bot.data.settings import load_settings  # ✅ bu yerda import qilamiz

    admins = await load_settings()
    for admin in admins:
        try:
            await bot.send_message(
                chat_id=admin,
                text="Bot ishga tushdi \n\n /admin panel",
                reply_markup=ReplyKeyboardRemove()
            )
        except Exception as err:
            print(f"Xatolik adminga yuborishda: {err}")
