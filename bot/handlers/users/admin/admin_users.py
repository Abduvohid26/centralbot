from datetime import datetime
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from bot.data.texts import text
from bot.filters.F import AdminFilter
from bot.keyboards.inline.admin import admin_back_menu
from bot.utils.database.functions import f_user

router = Router()


@router.callback_query(AdminFilter(), F.data == "admin_statistics")
async def handler_users(call: types.CallbackQuery, state: FSMContext):
    try:
        today_str = datetime.today().strftime('%Y-%m-%d')

        all_users = await f_user.count_users()
        active_users = await f_user.count_active_users()
        today_users = await f_user.get_daily_users_count(today_str)
        daily_users = await f_user.get_daily_updated_users_count(today_str)
        premium_users = await f_user.get_premium_users_count()

        statistics_text = text("admin_statistics").format(
            all_users=all_users,
            active_users=active_users,
            today_users=today_users,
            daily_users=daily_users,
            premium_users=premium_users
        )

        await call.message.edit_text(statistics_text, reply_markup=admin_back_menu)

    except Exception as e:
        print(f"❌ statistics error: {e}")
