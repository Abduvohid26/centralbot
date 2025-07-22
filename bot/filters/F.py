from typing import Union
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from bot.data.config import OWNER_ID
from bot.data.settings import load_settings
from bot.utils.database.functions.f_user import get_user_by_user_id

# Via bot orqali kelgan xabar
class ViaFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.via_bot is not None


# Faqat .env dagi super-admin (OWNER_ID)
class MyFilter(BaseFilter):
    async def __call__(self, obj: Union[Message, CallbackQuery]) -> bool:
        return obj.from_user.id == OWNER_ID

class AdminFilter(BaseFilter):
    async def __call__(self, obj: Union[Message, CallbackQuery]) -> bool:
        admins = await load_settings()
        print(obj.from_user.id in admins)
        return obj.from_user.id in admins

# CallbackData ichida keyword borligini tekshiradi
class CallBackFilter(BaseFilter):
    def __init__(self, kw: str) -> None:
        self.kw = kw

    async def __call__(self, call: CallbackQuery) -> bool:
        return self.kw in call.data
