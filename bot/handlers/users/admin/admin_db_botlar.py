import logging

from aiogram import Router, types, F
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards.inline.admin import generate_bot_list_keyboard, generate_single_bot_keyboard, \
    generate_delete_confirm_keyboard, generate_back_button
from bot.states.db_bots import AddSimpleBotFSM, EditBotFSM
from bot.utils.database.functions.f_dbbot import create_bot, delete_bot_by_username, update_bot_username

router = Router()

@router.callback_query(F.data == "admin_dbbots")
async def handle_admin_dbbots(callback: CallbackQuery):
    text, keyboard = await generate_bot_list_keyboard()
    await callback.message.edit_text(text=text, reply_markup=keyboard)

@router.callback_query(F.data == "admin_add_bots")
async def start_add_bot(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="🤖 Yangi bot username’ini yuboring (masalan: @mybot):",
        reply_markup= await generate_back_button("admin_dbbots")  # Ortga tugmasining callback_data si
    )
    await state.set_state(AddSimpleBotFSM.waiting_for_username)

@router.message(AddSimpleBotFSM.waiting_for_username)
async def save_bot_username(message: types.Message, state: FSMContext):
    username = message.text.strip()

    # @ bilan boshlanishi va bot bilan tugashi sharti
    if not (username.startswith("@") and username.lower().endswith("bot")):
        await message.answer("❗ Bot username `@` bilan boshlanishi va `bot` bilan tugashi kerak. Iltimos, qayta kiriting.")
        return

    try:
        await create_bot(username=username.lstrip("@"))
        await state.clear()

        text, keyboard = await generate_bot_list_keyboard()
        await message.answer(f"✅ Bot {username} qo‘shildi!\n\n{text}", reply_markup=keyboard)

    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")
        await state.clear()


@router.callback_query(F.data.startswith("admin_db_bot_"))
async def handle_single_bot(callback: CallbackQuery):
    username = callback.data.removeprefix("admin_db_bot_")

    text = f"🤖 Tanlangan bot: @{username}"
    keyboard = generate_single_bot_keyboard(username)

    await callback.message.edit_text(text=text, reply_markup=keyboard)

@router.callback_query(lambda c: c.data is not None and c.data.startswith("admindb_delete_bot_"))
async def ask_delete_confirmation(callback: CallbackQuery):
    username = callback.data.removeprefix("admindb_delete_bot_").strip()

    # Yangi klaviaturani chiqaramiz
    confirm_keyboard = generate_delete_confirm_keyboard(username)

    await callback.message.edit_text(
        text=f"🤔 <b>{username}</b> botini o‘chirishga ishonchingiz komilmi?",
        reply_markup=confirm_keyboard
    )
@router.callback_query(F.data.startswith("admindb_confirm_delete_bot_"))
async def delete_bot(callback: CallbackQuery):
    username = callback.data.removeprefix("admindb_confirm_delete_bot_")

    await delete_bot_by_username(username)

    # Yangilangan ro'yxatni chiqaramiz
    text, keyboard = await generate_bot_list_keyboard()
    await callback.message.edit_text(f"✅ @{username} bot bazadan o‘chirildi.\n\n{text}", reply_markup=keyboard)

@router.callback_query(F.data.startswith("admindb_cancel_delete_bot_"))
async def cancel_delete(callback: CallbackQuery):
    username = callback.data.removeprefix("admindb_cancel_delete_bot_")

    text = f"🤖 Tanlangan bot: @{username}"
    keyboard = generate_single_bot_keyboard(username)

    await callback.message.edit_text(text=text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("admindb_edit_bot_"))
async def ask_new_username(callback: CallbackQuery, state: FSMContext):
    old_username = callback.data.removeprefix("admindb_edit_bot_")

    # Eski username'ni FSM holatida saqlaymiz
    await state.update_data(old_username=old_username)

    # Javob xabari ortga tugmasi bilan
    await callback.message.edit_text(
        text=f"✏️ @{old_username} uchun yangi nom kiriting:",
        reply_markup=await generate_back_button(callback_data=f"admin_dbbots")
    )

    # Holatni belgilaymiz
    await state.set_state(EditBotFSM.waiting_for_new_username)

@router.message(EditBotFSM.waiting_for_new_username)
async def process_new_username(message: types.Message, state: FSMContext):
    new_username = message.text.strip().lstrip("@")

    data = await state.get_data()
    old_username = data.get("old_username")

    await update_bot_username(old_username, new_username)
    await state.clear()

    text = f"✅ Bot nomi yangilandi:\n🆕 @{new_username}"
    keyboard = generate_single_bot_keyboard(new_username)
    await message.answer(text, reply_markup=keyboard)
