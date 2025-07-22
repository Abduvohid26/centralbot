from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable, Union
from time import time


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit: float = 0.8):
        super().__init__()
        self.limit = limit
        self.last_called: Dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        now = time()

        last_time = self.last_called.get(user_id, 0)
        if now - last_time < self.limit:
            if isinstance(event, Message):
                await event.answer("Iltimos, biroz kuting...")
            elif isinstance(event, CallbackQuery):
                await event.answer("Iltimos, biroz kuting...", show_alert=False)
            return

        self.last_called[user_id] = now
        return await handler(event, data)
