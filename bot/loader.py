from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from bot.data.config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
storage = MemoryStorage()

dp = Dispatcher(storage=storage)
BOT_ID = None
BOT_USERNAME = None
async def set_bot_id():
    global BOT_ID
    global BOT_USERNAME
    me = await bot.get_me()
    BOT_ID = me.id
    BOT_USERNAME = me.username
# loader tayyor