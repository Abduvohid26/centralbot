from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from bot.filters.F import AdminFilter
from bot.keyboards.inline.admin import inline_telegramapp_list_keyboard, app_menu_buttons, \
    telegramapp_info_buttons, confirm_delete_telegramapp_buttons, back_admin_view
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from bot.states.telegramapp_states import AddTelegramAppFSM, EditTelegramAppFSM
from bot.utils.database.functions.f_telegramapp import create_telegram_app, get_telegram_app_by_id, \
    delete_telegram_app_by_id, get_all_telegram_apps, update_telegram_app, get_telegram_app_by_name

router = Router()

@router.callback_query(AdminFilter(), F.data == "admin_telegramapp")
async def open_telegramapp_menu(call: types.CallbackQuery):
    apps = await get_all_telegram_apps()

    if apps:
        kb = await inline_telegramapp_list_keyboard()
        await call.message.edit_text(
            "📋 Telegram APP ro‘yxati:",
            reply_markup=kb
        )
    else:
        await call.message.edit_text(
            "❗ Bazada hech qanday Telegram App yo‘q.",
            reply_markup=await inline_telegramapp_list_keyboard()
        )


@router.callback_query(F.data == "admin_add_telegramapp")
async def start_add_telegramapp(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.edit_text(
            "📝 Yangi Telegram API uchun nom kiriting:",
            reply_markup=app_menu_buttons
        )
    except TelegramBadRequest:
        await call.answer("ℹ️ Allaqachon shu holatda turibdi.")

    await state.set_state(AddTelegramAppFSM.name)


@router.message(AddTelegramAppFSM.name)
async def get_name(msg: types.Message, state: FSMContext):
    name = msg.text.strip()
    # Bazadan nomni tekshirish
    existing = await get_telegram_app_by_name(name)
    if existing:
        await msg.answer("❌ Bu nomli App allaqachon mavjud. Iltimos, boshqa nom kiriting.",
                         reply_markup=app_menu_buttons)
        return
    # Davom ettirish
    await state.update_data(name=name)
    await msg.answer("🔢 API_ID ni kiriting:", reply_markup=app_menu_buttons)
    await state.set_state(AddTelegramAppFSM.api_id)
@router.message(AddTelegramAppFSM.api_id)
async def get_api_id(msg: types.Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("❌ Iltimos, faqat raqam kiriting.")
        return
    await state.update_data(api_id=int(msg.text))
    await msg.answer("🔐 API_HASH ni kiriting:", reply_markup=app_menu_buttons)
    await state.set_state(AddTelegramAppFSM.api_hash)

@router.message(AddTelegramAppFSM.api_hash)
async def get_api_hash(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    api_hash = msg.text

    # Bazaga saqlash
    await create_telegram_app(
        name=data["name"],
        api_id=data["api_id"],
        api_hash=api_hash
    )
    await msg.answer("✅ Yangi Telegram App qo‘shildi.", reply_markup=app_menu_buttons)
    await state.clear()


@router.callback_query(F.data.startswith("admin_view_telegramapp_"))
async def view_telegramapp(call: types.CallbackQuery, state: FSMContext):
    app_id = int(call.data.split("_")[-1])
    app = await get_telegram_app_by_id(app_id)

    if not app:
        await call.answer("❌ Maʼlumot topilmadi", show_alert=True)
        return

    await state.update_data(app_id=app.id)

    text = (
        f"ℹ️ Telegram App haqida:\n\n"
        f"📱 Nomi: <b>{app.name}</b>\n"
        f"🆔 API_ID: <code>{app.api_id}</code>\n"
        f"🔐 API_HASH: <code>{app.api_hash}</code>"
    )

    try:
        await call.message.edit_text(
            text=text,
            reply_markup=telegramapp_info_buttons(app.id),
            parse_mode="HTML"
        )
    except TelegramBadRequest:
        pass


@router.callback_query(F.data.startswith("admin_delete_telegramapp_"))
async def ask_delete_confirmation(call: types.CallbackQuery):
    app_id = int(call.data.split("_")[-1])
    app = await get_telegram_app_by_id(app_id)

    if not app:
        await call.answer("❌ App topilmadi", show_alert=True)
        return

    msg = f"⚠️ <b>{app.name}</b> nomli Appʼni o‘chirmoqchimisiz?"

    try:
        await call.message.edit_text(msg, reply_markup=confirm_delete_telegramapp_buttons(app.id), parse_mode="HTML")
    except TelegramBadRequest:
        pass

@router.callback_query(F.data.startswith("confirm_delete_telegramapp_"))
async def delete_telegramapp(call: types.CallbackQuery):
    app_id = int(call.data.split("_")[-1])
    deleted = await delete_telegram_app_by_id(app_id)

    if deleted:
        apps = await get_all_telegram_apps()
        if apps:
            keyboard = await inline_telegramapp_list_keyboard()
            await call.message.edit_text("✅ App o‘chirildi.\n\n📋 Yangilangan ro‘yxat:", reply_markup=keyboard)
        else:
            await call.message.edit_text("✅ App o‘chirildi.\n\n❗ Bazada hech qanday Telegram App qolmadi.")
    else:
        await call.answer("❌ O‘chirilmadi", show_alert=True)
@router.callback_query(F.data.startswith("admin_app_name"))
async def edit_name_start(call: types.CallbackQuery, state: FSMContext):
    app_id = int(call.message.reply_markup.inline_keyboard[-1][0].callback_data.split("_")[-1])
    await state.update_data(app_id=app_id)
    await call.message.edit_text("📝 Yangi nomni kiriting:", reply_markup=back_admin_view(app_id))
    await state.set_state(EditTelegramAppFSM.name)

@router.callback_query(F.data.startswith("admin_app_id"))
async def edit_api_id_start(call: types.CallbackQuery, state: FSMContext):
    app_id = int(call.message.reply_markup.inline_keyboard[-1][0].callback_data.split("_")[-1])
    await state.update_data(app_id=app_id)
    await call.message.edit_text("🔢 Yangi API_ID ni kiriting:", reply_markup=back_admin_view(app_id))
    await state.set_state(EditTelegramAppFSM.api_id)

@router.callback_query(F.data.startswith("admin_app_apihash"))
async def edit_api_hash_start(call: types.CallbackQuery, state: FSMContext):
    app_id = int(call.message.reply_markup.inline_keyboard[-1][0].callback_data.split("_")[-1])
    await state.update_data(app_id=app_id)
    await call.message.edit_text("🔐 Yangi API_HASH ni kiriting:", reply_markup=back_admin_view(app_id))
    await state.set_state(EditTelegramAppFSM.api_hash)

@router.message(EditTelegramAppFSM.name)
async def set_name(msg: Message, state: FSMContext):
    data = await state.get_data()
    await update_telegram_app(data["app_id"], name=msg.text)
    await state.clear()

    app = await get_telegram_app_by_id(data["app_id"])

    await msg.answer("✅ Nomi yangilandi.")
    await msg.answer(
        text=(
            f"ℹ️ Telegram App haqida:\n\n"
            f"📱 Nomi: <b>{app.name}</b>\n"
            f"🆔 API_ID: <code>{app.api_id}</code>\n"
            f"🔐 API_HASH: <code>{app.api_hash}</code>"
        ),
        reply_markup=telegramapp_info_buttons(app.id),
        parse_mode="HTML"
    )

@router.message(EditTelegramAppFSM.api_id)
async def set_api_id(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("❌ Iltimos, faqat raqam kiriting.")
        return

    data = await state.get_data()
    await update_telegram_app(data["app_id"], api_id=int(msg.text))
    await state.clear()

    app = await get_telegram_app_by_id(data["app_id"])

    await msg.answer("✅ API_ID yangilandi.")
    await msg.answer(
        text=(
            f"ℹ️ Telegram App haqida:\n\n"
            f"📱 Nomi: <b>{app.name}</b>\n"
            f"🆔 API_ID: <code>{app.api_id}</code>\n"
            f"🔐 API_HASH: <code>{app.api_hash}</code>"
        ),
        reply_markup=telegramapp_info_buttons(app.id),
        parse_mode="HTML"
    )

@router.message(EditTelegramAppFSM.api_hash)
async def set_api_hash(msg: Message, state: FSMContext):
    data = await state.get_data()
    await update_telegram_app(data["app_id"], api_hash=msg.text)
    await state.clear()

    app = await get_telegram_app_by_id(data["app_id"])

    await msg.answer("✅ API_HASH yangilandi.")
    await msg.answer(
        text=(
            f"ℹ️ Telegram App haqida:\n\n"
            f"📱 Nomi: <b>{app.name}</b>\n"
            f"🆔 API_ID: <code>{app.api_id}</code>\n"
            f"🔐 API_HASH: <code>{app.api_hash}</code>"
        ),
        reply_markup=telegramapp_info_buttons(app.id),
        parse_mode="HTML"
    )
