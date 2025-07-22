from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from bot.services.external_service_bot import register_media_handler

async def run_bot_with_token(bot_token: str, link: str, client_id: int):
    bot = Bot(token=bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    register_media_handler(dp, link, client_id)
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        pass
    finally:
        await bot.session.close()