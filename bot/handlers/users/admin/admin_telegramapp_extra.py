from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from bot.filters.F import AdminFilter
from bot.keyboards.inline.admin import inline_telegramapp_list_keyboard_extra, app_menu_buttons_extra, \
    telegramapp_info_buttons_extra, confirm_delete_telegramapp_buttons_extra, back_admin_view_extra
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from bot.states.telegramapp_states import AddTelegramAppFSMExtra, EditTelegramAppFSMExtra
from bot.utils.database.functions.f_telegramapp import create_telegram_app_extra, get_telegram_app_by_id_extra, \
    delete_telegram_app_by_id_extra, get_all_telegram_apps_extra, update_telegram_app_extra, get_telegram_app_by_name_extra, get_all_telegram_apps_extra

router = Router()

@router.callback_query(AdminFilter(), F.data == "admin_telegramapp_extra")
async def open_telegramapp_menu(call: types.CallbackQuery):
    apps = await get_all_telegram_apps_extra()

    if apps:
        kb = await inline_telegramapp_list_keyboard_extra()
        await call.message.edit_text(
            "📋 Telegram APP ro‘yxati:",
            reply_markup=kb
        )
    else:
        await call.message.edit_text(
            "❗ Bazada hech qanday Telegram App yo‘q.",
            reply_markup=await inline_telegramapp_list_keyboard_extra()
        )


@router.callback_query(F.data == "admin_add_telegramapp_extra")
async def start_add_telegramapp(call: types.CallbackQuery, state: FSMContext):
    print("Step2")

    try:
        await call.message.edit_text(
            "📝 Yangi Telegram API uchun nom kiriting:",
            reply_markup=app_menu_buttons_extra
        )
    except TelegramBadRequest:
        await call.answer("ℹ️ Allaqachon shu holatda turibdi.")

    await state.set_state(AddTelegramAppFSMExtra.name)


@router.message(AddTelegramAppFSMExtra.name)
async def get_name(msg: types.Message, state: FSMContext):
    print("Step3")
    name = msg.text.strip()
    # Bazadan nomni tekshirish
    existing = await get_telegram_app_by_name_extra(name)
    if existing:
        await msg.answer("❌ Bu nomli App allaqachon mavjud. Iltimos, boshqa nom kiriting.",
                         reply_markup=app_menu_buttons_extra)
        return
    # Davom ettirish
    await state.update_data(name=name)
    await msg.answer("🔢 API_ID ni kiriting:", reply_markup=app_menu_buttons_extra)
    await state.set_state(AddTelegramAppFSMExtra.api_id)


@router.message(AddTelegramAppFSMExtra.api_id)
async def get_api_id(msg: types.Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("❌ Iltimos, faqat raqam kiriting.")
        return
    await state.update_data(api_id=int(msg.text))
    await msg.answer("🔐 API_HASH ni kiriting:", reply_markup=app_menu_buttons_extra)
    await state.set_state(AddTelegramAppFSMExtra.api_hash)

@router.message(AddTelegramAppFSMExtra.api_hash)
async def get_api_hash(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    api_hash = msg.text

    # Bazaga saqlash
    await create_telegram_app_extra(
        name=data["name"],
        api_id=data["api_id"],
        api_hash=api_hash
    )
    await msg.answer("✅ Yangi Telegram App qo‘shildi.", reply_markup=app_menu_buttons_extra)
    await state.clear()


@router.callback_query(F.data.startswith("admin_extra_view_telegramapp_"))
async def view_telegramapp(call: types.CallbackQuery, state: FSMContext):
    app_id = int(call.data.split("_")[-1])
    print(app_id, "app_id")
    app = await get_telegram_app_by_id_extra(app_id)

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
            reply_markup=telegramapp_info_buttons_extra(app.id),
            parse_mode="HTML"
        )
    except TelegramBadRequest:
        pass




@router.callback_query(F.data.startswith("extra_confirm_delete_userbot_"))
async def ask_delete_confirmation(call: types.CallbackQuery):
    app_id = int(call.data.split("_")[-1])
    print(app_id, "app_id")
    app = await get_telegram_app_by_id_extra(app_id)

    if not app:
        await call.answer("❌ App topilmadi", show_alert=True)
        return

    msg = f"⚠️ <b>{app.name}</b> nomli Appʼni o‘chirmoqchimisiz?"

    try:
        await call.message.edit_text(msg, reply_markup=confirm_delete_telegramapp_buttons_extra(app.id), parse_mode="HTML")
    except TelegramBadRequest:
        pass

@router.callback_query(F.data.startswith("extra_confirm_delete_telegramapp_"))
async def delete_telegramapp(call: types.CallbackQuery):
    app_id = int(call.data.split("_")[-1])
    print(app_id, "app_id1")
    deleted = await delete_telegram_app_by_id_extra(app_id)
    print(deleted, "deleted")
    if deleted:
        apps = await get_all_telegram_apps_extra()
        if apps:
            keyboard = await inline_telegramapp_list_keyboard_extra()
            await call.message.edit_text("✅ App o‘chirildi.\n\n📋 Yangilangan ro‘yxat:", reply_markup=keyboard)
        else:
            await call.message.edit_text("✅ App o‘chirildi.\n\n❗ Bazada hech qanday Telegram App qolmadi.")
    else:
        await call.answer("❌ O‘chirilmadi", show_alert=True)


@router.callback_query(F.data.startswith("admin_app_extra_name"))
async def edit_name_start(call: types.CallbackQuery, state: FSMContext):
    app_id = int(call.message.reply_markup.inline_keyboard[-1][0].callback_data.split("_")[-1])
    await state.update_data(app_id=app_id)
    print("new app id", app_id)
    await call.message.edit_text("📝 Yangi nomni kiriting:", reply_markup=back_admin_view_extra(app_id))
    await state.set_state(EditTelegramAppFSMExtra.name)


@router.callback_query(F.data.startswith("admin_app_extra_id"))
async def edit_api_id_start(call: types.CallbackQuery, state: FSMContext):
    app_id = int(call.message.reply_markup.inline_keyboard[-1][0].callback_data.split("_")[-1])
    await state.update_data(app_id=app_id)
    await call.message.edit_text("🔢 Yangi API_ID ni kiriting:", reply_markup=back_admin_view_extra(app_id))
    await state.set_state(EditTelegramAppFSMExtra.api_id)

@router.callback_query(F.data.startswith("admin_app_extra_apihash"))
async def edit_api_hash_start(call: types.CallbackQuery, state: FSMContext):
    app_id = int(call.message.reply_markup.inline_keyboard[-1][0].callback_data.split("_")[-1])
    await state.update_data(app_id=app_id)
    await call.message.edit_text("🔐 Yangi API_HASH ni kiriting:", reply_markup=back_admin_view_extra(app_id))
    await state.set_state(EditTelegramAppFSMExtra.api_hash)

@router.message(EditTelegramAppFSMExtra.name)
async def set_name(msg: Message, state: FSMContext):
    data = await state.get_data()
    await update_telegram_app_extra(data["app_id"], name=msg.text)
    await state.clear()

    app = await get_telegram_app_by_id_extra(data["app_id"])

    await msg.answer("✅ Nomi yangilandi.")
    await msg.answer(
        text=(
            f"ℹ️ Telegram App haqida:\n\n"
            f"📱 Nomi: <b>{app.name}</b>\n"
            f"🆔 API_ID: <code>{app.api_id}</code>\n"
            f"🔐 API_HASH: <code>{app.api_hash}</code>"
        ),
        reply_markup=telegramapp_info_buttons_extra(app.id),
        parse_mode="HTML"
    )

@router.message(EditTelegramAppFSMExtra.api_id)
async def set_api_id(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("❌ Iltimos, faqat raqam kiriting.")
        return

    data = await state.get_data()
    await update_telegram_app_extra(data["app_id"], api_id=int(msg.text))
    await state.clear()

    app = await get_telegram_app_by_id_extra(data["app_id"])

    await msg.answer("✅ API_ID yangilandi.")
    await msg.answer(
        text=(
            f"ℹ️ Telegram App haqida:\n\n"
            f"📱 Nomi: <b>{app.name}</b>\n"
            f"🆔 API_ID: <code>{app.api_id}</code>\n"
            f"🔐 API_HASH: <code>{app.api_hash}</code>"
        ),
        reply_markup=telegramapp_info_buttons_extra(app.id),
        parse_mode="HTML"
    )

@router.message(EditTelegramAppFSMExtra.api_hash)
async def set_api_hash(msg: Message, state: FSMContext):
    data = await state.get_data()
    await update_telegram_app_extra(data["app_id"], api_hash=msg.text)
    await state.clear()

    app = await get_telegram_app_by_id_extra(data["app_id"])

    await msg.answer("✅ API_HASH yangilandi.")
    await msg.answer(
        text=(
            f"ℹ️ Telegram App haqida:\n\n"
            f"📱 Nomi: <b>{app.name}</b>\n"
            f"🆔 API_ID: <code>{app.api_id}</code>\n"
            f"🔐 API_HASH: <code>{app.api_hash}</code>"
        ),
        reply_markup=telegramapp_info_buttons_extra(app.id),
        parse_mode="HTML"
    )
