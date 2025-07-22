from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from bot.filters.F import AdminFilter
from bot.keyboards.inline.admin import build_channels_inline_keyboard, admin_back_menu, build_channel_detail_keyboard, \
    build_channel_delete_confirm_keyboard
from bot.states.channel_userbot import AddChannelState, EditChannelState
from bot.utils.database.functions.f_channel_userbot import create_channel_userbot, get_all_channels, \
    get_channel_by_chat_id, delete_channel_by_chat_id, update_channel_userbot

router = Router()

@router.callback_query(AdminFilter(), F.data == "admin_media_channel")
async def admin_media_channel_handler(call: types.CallbackQuery):

    channels = await get_all_channels()
    kb = build_channels_inline_keyboard(channels)

    if not channels:
        await call.message.edit_text(
            "Hali kanal mavjud emas.",
            reply_markup=kb
        )
    else:
        await call.message.edit_text(
            "Kanallar ro‘yxati:",
            reply_markup=kb
        )

@router.callback_query(lambda c: c.data == "admin_channel_userbot_add")
async def admin_channel_add_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Kanal nomini kiriting:", reply_markup=admin_back_menu)
    await state.set_state(AddChannelState.waiting_for_channel_name)

@router.message(AddChannelState.waiting_for_channel_name)
async def add_channel_name_handler(message: types.Message, state: FSMContext):
    channel_name = message.text.strip()
    await state.update_data(channel_name=channel_name)
    await message.answer("Kanal chat_id sini kiriting:", reply_markup=admin_back_menu)
    await state.set_state(AddChannelState.waiting_for_channel_chat_id)

@router.message(AddChannelState.waiting_for_channel_chat_id)
async def add_channel_chat_id_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    channel_name = data.get("channel_name")
    try:
        channel_chat_id = int(message.text.strip())
    except ValueError:
        await message.answer("Chat ID faqat raqam bo‘lishi kerak. Qaytadan kiriting:", reply_markup=admin_back_menu)
        return

    await create_channel_userbot(channel_chat_id=channel_chat_id, channel_name=channel_name)
    await message.answer("Kanal muvaffaqiyatli qo‘shildi✅", reply_markup=admin_back_menu)
    await state.clear()
@router.callback_query(lambda c: c.data == "admin_channel_userbot_back")
async def back_to_channels_list(call: types.CallbackQuery):
    channels = await get_all_channels()
    kb = build_channels_inline_keyboard(channels)
    await call.message.edit_text("Kanallar ro‘yxati:", reply_markup=kb)

@router.callback_query(lambda c: c.data.startswith("admin_channel_detail:"))
async def show_channel_detail(call: types.CallbackQuery):
    channel_chat_id = int(call.data.split(":")[1])
    channel = await get_channel_by_chat_id(channel_chat_id)
    if not channel:
        await call.message.edit_text("Kanal topilmadi.")
        return
    kb = build_channel_detail_keyboard(channel)
    await call.message.edit_text(
        "Kanal tafsilotlari:",  # Qisqa matn, faqat tugmalar pastda
        reply_markup=kb
    )

@router.callback_query(lambda c: c.data.startswith("admin_channel_delete:"))
async def confirm_delete_channel_handler(call: types.CallbackQuery):
    channel_chat_id = int(call.data.split(":")[1])
    kb = build_channel_delete_confirm_keyboard(channel_chat_id)
    await call.message.edit_text(
        "Rostdan ham ushbu kanalni o‘chirasizmi?",
        reply_markup=kb
    )
@router.callback_query(lambda c: c.data == "admin_channel_userbot_back")
async def back_to_channels_list(call: types.CallbackQuery):
    channels = await get_all_channels()
    kb = build_channels_inline_keyboard(channels)
    await call.message.edit_text("Kanallar ro‘yxati:", reply_markup=kb)

@router.callback_query(lambda c: c.data.startswith("admin_channel_delete_confirm:"))
async def delete_channel_handler(call: types.CallbackQuery):
    channel_chat_id = int(call.data.split(":")[1])
    channel = await get_channel_by_chat_id(channel_chat_id)
    if not channel:
        await call.message.edit_text("Kanal topilmadi yoki allaqachon o‘chirilgan.", reply_markup=admin_back_menu)
        return

    channel_name = channel.channel_name
    await delete_channel_by_chat_id(channel_chat_id)

    channels = await get_all_channels()
    kb = build_channels_inline_keyboard(channels)
    await call.message.edit_text(
        f"✅ \"{channel_name}\" kanali muvaffaqiyatli o‘chirildi!\n\nKanallar ro‘yxati:",
        reply_markup=kb
    )
@router.callback_query(lambda c: c.data.startswith("edit_channel_name:"))
async def prompt_new_channel_name(call: types.CallbackQuery, state: FSMContext):
    channel_id = int(call.data.split(":")[1])
    await call.message.edit_text("Yangi kanal nomini kiriting:", reply_markup=admin_back_menu)
    await state.set_state(EditChannelState.waiting_for_channel_name)
    await state.update_data(channel_id=channel_id)

@router.message(EditChannelState.waiting_for_channel_name)
async def set_new_channel_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    channel_id = data.get("channel_id")
    new_name = message.text.strip()
    await update_channel_userbot(channel_id, channel_name=new_name)
    channel = await get_channel_by_chat_id(channel_id)
    kb = build_channel_detail_keyboard(channel)
    await message.answer("✅ Kanal nomi muvaffaqiyatli o‘zgartirildi!", reply_markup=kb)
    await state.clear()

@router.callback_query(lambda c: c.data.startswith("edit_channel_chat_id:"))
async def prompt_new_channel_chat_id(call: types.CallbackQuery, state: FSMContext):
    channel_id = int(call.data.split(":")[1])
    await call.message.edit_text("Yangi chat_id ni kiriting:", reply_markup=admin_back_menu)
    await state.set_state(EditChannelState.waiting_for_channel_chat_id)
    await state.update_data(channel_id=channel_id)

@router.message(EditChannelState.waiting_for_channel_chat_id)
async def set_new_channel_chat_id(message: types.Message, state: FSMContext):
    data = await state.get_data()
    old_channel_id = data.get("channel_id")
    try:
        new_chat_id = int(message.text.strip())
    except ValueError:
        await message.answer("Chat ID raqam bo‘lishi kerak. Qayta kiriting.", reply_markup=admin_back_menu)
        return

    await update_channel_userbot(old_channel_id, new_chat_id=new_chat_id)
    channel = await get_channel_by_chat_id(new_chat_id)
    kb = build_channel_detail_keyboard(channel)
    await message.answer("✅ Chat ID muvaffaqiyatli o‘zgartirildi!", reply_markup=kb)
    await state.clear()
