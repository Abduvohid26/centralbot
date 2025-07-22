from aiogram import Router, F
from aiogram.types import CallbackQuery
from bot.filters.F import AdminFilter
from bot.keyboards.inline.admin import admin_back_menu
from bot.utils.database.functions.f_stat_link import get_social_network_stats
from bot.utils.database.models import async_session

router = Router()

@router.callback_query(AdminFilter(), F.data == "admin_link_statestika")
async def show_link_statistika(call: CallbackQuery):
    async with async_session() as session:
        stat_dict = await get_social_network_stats(session)
        if not stat_dict:
            await call.message.edit_text("Hali hech qanday link statistikasi yo‘q.", reply_markup=admin_back_menu)
            return

        msg = "<b>🌐 Ijtimoiy tarmoqlar link statistikasi:</b>\n\n"
        for name, count in stat_dict.items():
            if count > 0:
                msg += f"🔹 <b>{name}:</b> {count} ta\n"
        if all(v == 0 for v in stat_dict.values()):
            msg += "Hech bir tarmoqqa link yuborilmagan."

        await call.message.edit_text(
            msg,
            parse_mode="HTML",
            reply_markup=admin_back_menu
        )