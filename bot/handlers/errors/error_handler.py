# bot/handlers/errors/error_handler.py
import logging
from aiogram.types import TelegramObject
from aiogram.exceptions import (
    TelegramAPIError,
    TelegramRetryAfter,
    TelegramUnauthorizedError,
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramNotFound,
)

async def error_handler(event: TelegramObject, exception: Exception) -> None:
    if isinstance(exception, TelegramRetryAfter):
        logging.warning(f"❗ Flood control: RetryAfter: {exception}")
        return

    if isinstance(exception, TelegramUnauthorizedError):
        logging.warning(f"❗ Unauthorized: {exception}")
        return

    if isinstance(exception, TelegramForbiddenError):
        logging.warning(f"❗ Forbidden: {exception}")
        return

    if isinstance(exception, TelegramNotFound):
        logging.warning(f"❗ Not found (chat/user/message): {exception}")
        return

    if isinstance(exception, TelegramBadRequest):
        logging.warning(f"❗ Bad request: {exception}")
        return

    if isinstance(exception, TelegramAPIError):
        logging.warning(f"❗ General TelegramAPIError: {exception}")
        return

    logging.exception(f"❗ Unknown exception: {exception}\nEvent: {event}")
