from bot.loader import bot, dp, set_bot_id
from bot.utils.set_bot_commands import set_default_commands
from bot.utils.notify_admins import on_startup_notify
from bot.utils.database.models import engine, Base, create_database, create_tables

async def on_startup():
    await create_database()
    await create_tables()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await set_bot_id()
    await set_default_commands(bot)
    await on_startup_notify(bot)

async def run_bot():
    from bot.handlers.users.main import routers as user_main_routers
    from bot.handlers.errors.error_handler import error_handler
    from bot.handlers.users.admin import routers as admin_main_routers

    for r in user_main_routers:
        dp.include_router(r)
    for r in admin_main_routers:
        dp.include_router(r)

    dp.errors.register(error_handler)
    await on_startup()
    await dp.start_polling(bot)
