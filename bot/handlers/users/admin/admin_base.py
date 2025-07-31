from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from bot.data.texts import text
from bot.filters.F import AdminFilter
from bot.keyboards.inline.admin import admin_main_menu


# Router obyekti
router = Router()

# /admin komandasi uchun handler
@router.message(AdminFilter(), Command("admin"))
async def admin_start_message(message: types.Message, state: FSMContext):
    fullname = message.from_user.full_name
    admin_text = text("admin_start").format(fullname=fullname)
    await message.answer(admin_text, reply_markup=admin_main_menu)
    await state.clear()

# "admin_back" callback uchun handler
@router.callback_query(AdminFilter(), F.data == "admin_back")
async def admin_start_callback(call: types.CallbackQuery, state: FSMContext):
    fullname = call.from_user.full_name
    admin_text = text("admin_start").format(fullname=fullname)

    await call.message.edit_text(admin_text, reply_markup=admin_main_menu)
    await state.clear()



@router.callback_query(AdminFilter(), F.data == "admin_back_extra")

@router.callback_query(AdminFilter(), F.data == "admin_back_extra")
async def admin_start_callback(call: types.CallbackQuery, state: FSMContext):
    fullname = call.from_user.full_name
    admin_text = text("admin_start").format(fullname=fullname)

    await call.message.edit_text(admin_text, reply_markup=admin_main_menu)
    await state.clear()