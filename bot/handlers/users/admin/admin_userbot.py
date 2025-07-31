from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError

from api.routes.media import fetch_allowed_usernames
from bot.filters.F import AdminFilter
from bot.keyboards.inline.admin import inline_userbot_list_keyboard, choose_app_buttons, confirm_delete_userbot_buttons, \
    admin_back_menu
from bot.states.userbot_states import AddUserBotFSM
from bot.utils.database.functions.f_telegramapp import available_telegram_apps, get_telegram_app_by_id
from bot.utils.database.functions.f_userbot import get_all_user_bots, save_user_bot_to_db, delete_userbot_by_id, \
    get_all_userbots

router = Router()

@router.callback_query(AdminFilter(), F.data == "admin_userbot")
async def open_userbot_menu(call: types.CallbackQuery):
    bots = await get_all_user_bots()
    text, keyboard = inline_userbot_list_keyboard(bots, page=1)
    await call.message.edit_text(text, reply_markup=keyboard)

# 1. Boshlash - app tanlash
@router.callback_query(F.data == "admin_add_userbot")
async def start_add_userbot(call: types.CallbackQuery, state: FSMContext):
    apps = await available_telegram_apps()
    if not apps:
        await call.message.answer("❌ Mavjud Telegram App yo‘q yoki barchasi to‘la.", reply_markup=admin_back_menu)
        return

    await call.message.edit_text(
        "📲 Qaysi Telegram App orqali ulanmoqchisiz?",
        reply_markup=choose_app_buttons(apps)
    )
    await state.set_state(AddUserBotFSM.choose_app)

# 2. App tanlandi
@router.callback_query(F.data.startswith("choose_app_"))
async def handle_choose_app(call: types.CallbackQuery, state: FSMContext):
    app_id = int(call.data.split("_")[-1])
    app = await get_telegram_app_by_id(app_id)

    if not app:
        await call.answer("❌ App topilmadi", show_alert=True)
        return

    await state.update_data(
        app_id=app.api_id,
        app_hash=app.api_hash,
        telegram_app_id=app.id
    )

    await call.message.edit_text("📞 Telefon raqamingizni kiriting (masalan: +998901234567):")
    await state.set_state(AddUserBotFSM.phone)
# 3. Telefon raqami olindi, kod yuboriladi
@router.message(AddUserBotFSM.phone)
async def handle_phone(msg: types.Message, state: FSMContext):
    phone = msg.text.strip()
    data = await state.get_data()

    client = TelegramClient(StringSession(), data["app_id"], data["app_hash"])
    await client.connect()

    try:
        sent = await client.send_code_request(phone)
        print(phone, ">>>>raqamiga kod yuborildi")
        # disconnect qilmaysiz hali
        await state.update_data(
            phone=phone,
            code_hash=sent.phone_code_hash,
            temp_session=client.session.save()
        )
        await msg.answer(
            f"📨 Telegram yuborgan kodni kiriting:\nTelefon: {phone}\nAPI ID: {data['app_id']}\nAPI HASH: {data['app_hash']}"
        )

        await state.set_state(AddUserBotFSM.code)

    except Exception as e:
        await msg.answer(f"❌ Xatolik: {e}")
        await client.disconnect()

# 4. Kod kiritildi, login qilinadi

@router.message(AddUserBotFSM.code)
async def handle_code(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    client = TelegramClient(StringSession(data["temp_session"]), data["app_id"], data["app_hash"])
    await client.connect()
    try:
        await client.sign_in(
            phone=data["phone"],
            code=msg.text.strip(),
            phone_code_hash=data["code_hash"]
        )
        session_str = client.session.save()
        me = await client.get_me()

        await save_user_bot_to_db(
            phone=data["phone"],
            session_string=session_str,
            telegram_user_id=me.id,
            telegram_app_id=data["telegram_app_id"]
        )

        await msg.answer("✅ User bot muvaffaqiyatli qo‘shildi.")

        # 🔥 API dan ruxsat etilgan botlar ro'yxatini olamiz
        allowed_bot_usernames = await fetch_allowed_usernames()

        # 🔁 Har biriga /start yuboramiz
        for bot_username in allowed_bot_usernames:
            try:
                await client.send_message(bot_username, "/start")
                print(f"✅ {me.username} → /start yuborildi → @{bot_username}")
            except Exception as send_err:
                print(f"❌ {me.username} → Xatolik @{bot_username} ga yuborishda: {send_err}")

        await state.clear()
    except SessionPasswordNeededError:
        await state.update_data(temp_session=client.session.save())
        await msg.answer("🔐 2FA parol o‘rnatilgan. Parolni kiriting:")
        await state.set_state(AddUserBotFSM.password)

    except Exception as e:
        await msg.answer(f"❌ Xatolik: {e}")
        await state.clear()

    finally:
        await client.disconnect()


@router.message(AddUserBotFSM.password)
async def handle_password(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    client = TelegramClient(StringSession(data["temp_session"]), data["app_id"], data["app_hash"])
    await client.connect()

    try:
        await client.sign_in(password=msg.text.strip())
        session_str = client.session.save()
        me = await client.get_me()

        # 🧠 Bazaga saqlaymiz
        await save_user_bot_to_db(
            phone=data["phone"],
            session_string=session_str,
            telegram_user_id=me.id,
            telegram_app_id=data["telegram_app_id"]
        )

        await msg.answer("✅ User bot 2FA bilan muvaffaqiyatli qo‘shildi.")

        # ✅ API dan allowed botlar ro'yxatini olib chiqamiz
        allowed_bot_usernames = await fetch_allowed_usernames()

        # 🔁 Har biriga start yuboramiz
        for bot_username in allowed_bot_usernames:
            try:
                await client.send_message(bot_username, "/start")
                print(f"✅ {me.username} → /start yuborildi → @{bot_username}")
            except Exception as send_err:
                print(f"❌ {me.username} → Xatolik @{bot_username} ga yuborishda: {send_err}")

    except Exception as e:
        await msg.answer(f"❌ Parol noto‘g‘ri yoki xatolik: {e}")
    finally:
        await client.disconnect()
        await state.clear()
@router.callback_query(F.data.startswith("view_userbot_"))
async def confirm_userbot_delete(call: types.CallbackQuery):
    bot_id = int(call.data.split("_")[-1])
    # Optional: tekshiruv bazadan topiladimi
    await call.message.edit_text(
        f"❗ Rostdan ham bu user botni o‘chirmoqchimisiz?",
        reply_markup=confirm_delete_userbot_buttons(bot_id)
    )
@router.callback_query(F.data.startswith("confirm_delete_userbot_"))
async def delete_userbot(call: types.CallbackQuery):
    bot_id = int(call.data.split("_")[-1])
    deleted = await delete_userbot_by_id(bot_id)  # Sizning DB funksiyangiz bo‘lishi kerak

    if deleted:
        bots = await get_all_user_bots()
        text, keyboard = inline_userbot_list_keyboard(bots, page=1)
        await call.message.edit_text(f"✅ User bot o‘chirildi.\n\n{text}", reply_markup=keyboard)
    else:
        await call.answer("❌ O‘chirishda xatolik yuz berdi", show_alert=True)
@router.callback_query(F.data == "cancel_delete_userbot")
async def cancel_userbot_delete(call: types.CallbackQuery):
    bots = await get_all_user_bots()
    text, keyboard = inline_userbot_list_keyboard(bots, page=1)
    await call.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("userbot_page_"))
async def handle_userbot_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[-1])

    # Bu yerdan bazadan botlarni olib kelish kerak
    bots = await get_all_userbots()  # Buning o‘rniga o‘z funksiyangizni qo‘ying

    # Klaviatura va matnni yaratish
    text, kb = inline_userbot_list_keyboard(bots=bots, page=page)

    try:
        await callback.message.edit_text(text=text, reply_markup=kb)
    except Exception as e:
        await callback.answer("Xatolik yuz berdi")
        print(e)

    await callback.answer()