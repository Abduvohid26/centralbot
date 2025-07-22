from aiogram import Bot
from aiogram.types import ChatMember
from typing import Union


async def check(user_id: int, channel: Union[int, str]) -> bool:
    bot = Bot.get_current()
    try:
        member: ChatMember = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        return member.status in ("member", "creator", "administrator")
    except Exception as e:
        print(f"check() xatolik: {e}")
        return False
