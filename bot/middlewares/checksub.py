from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from typing import Callable, Dict, Any, Awaitable, Union
from bot.data.config import toshkent_now
from bot.data.texts import text
from bot.middlewares.misc import check_status
from bot.utils.database.functions import f_user

class BigBrother(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:

        user_id = event.from_user.id

        # ✅ 1. Yangilanish vaqti
        await f_user.update_user(user_id, updated_at=toshkent_now())

        # ✅ 2. Guruhlardan chiqish
        if hasattr(event, "chat") and "group" in event.chat.type:
            return  # Guruhdan kelgan bo‘lsa, bekor qilinadi

        # ✅ 3. Obuna tekshiruvi
        status, keyboard = await check_status(user_id)
        if not status:
            markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

            if isinstance(event, Message):
                await event.answer(
                    text("user_subscribe_request"),
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
                return  # Handlerga o‘tkazilmaydi

            elif isinstance(event, CallbackQuery):
                if not event.data.startswith(("district:", "region:")):
                    try:
                        await event.message.edit_text(
                            text("user_subscribe_request"),
                            reply_markup=markup,
                            disable_web_page_preview=True
                        )
                    except:
                        try:
                            await event.answer("⚠️ Kanalga a'zo bo'ling", cache_time=0)
                        except:
                            pass
                    return

        # ✅ 4. Hammasi joyida bo‘lsa — davom etadi
        return await handler(event, data)
