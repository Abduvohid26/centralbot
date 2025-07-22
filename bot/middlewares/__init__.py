from aiogram import Dispatcher
from .throttling import ThrottlingMiddleware
from .checksub import BigBrother

def setup_middlewares(dp: Dispatcher):
    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())

    dp.message.middleware(BigBrother())
    dp.callback_query.middleware(BigBrother())
