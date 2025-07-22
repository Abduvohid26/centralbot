from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from bot.filters.F import AdminFilter
from bot.keyboards.inline.admin import inline_admin_list_keyboard, admin_confirm_kb, admin_action_kb
from bot.states.admin_add_admin import AdminStates
from bot.utils.database.functions.f_user import get_user_byid, update_user, get_user_by_user_id, update_user_admin

router = Router()

@router.callback_query(AdminFilter(), F.data == "admin_admins")  # masalan, bu callback
async def show_admins(callback: CallbackQuery):
    markup = await inline_admin_list_keyboard()
    await callback.message.edit_text("📋 Adminlar ro‘yxati:", reply_markup=markup)

@router.callback_query(AdminFilter(), F.data == "admin_add_admin")
async def add_admin_start(callback: CallbackQuery, state: FSMContext):
    # Boshlanganda - userdan ID so‘radik
    await callback.message.edit_text("🔍 Iltimos, admin qilmoqchi bo‘lgan userning <b>user_id</b> sini yuboring:")
    await state.set_state(AdminStates.waiting_for_user_id)


@router.message(AdminStates.waiting_for_user_id)
async def process_new_admin(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text.isdigit():
        await message.answer("❌ Iltimos, faqat raqam kiriting.")
        return

    user_id = int(text)
    user = await get_user_by_user_id(user_id)
    if not user:
        await message.answer("❌ Bunday foydalanuvchi topilmadi.")
        return

    # is_admin = True qilib yangilash
    success = await update_user_admin(user_id, is_admin=True)
    await state.clear()

    if success:
        await message.answer(f"✅ User <b>{user_id}</b> endi admin qilindi!", parse_mode="HTML")
    else:
        await message.answer("❌ Yangilashda xatolik yuz berdi.")
        return

    # Yangilangan adminlar ro‘yxatini ko‘rsatish
    markup = await inline_admin_list_keyboard()
    await message.answer("📋 Yangilangan adminlar ro‘yxati:", reply_markup=markup)


@router.callback_query(AdminFilter(), F.data.startswith("admin_view_user_"))
async def view_admin(callback: CallbackQuery):
    user_id = int(callback.data.rsplit("_", 1)[1])
    kb = admin_action_kb(user_id)
    await callback.message.edit_text(
        f"👤 Admin: <b>{user_id}</b>\n\nNimeni amalga oshirmoqchisiz?",
        reply_markup=kb,
        parse_mode="HTML"
    )

@router.callback_query(AdminFilter(), F.data.startswith("admin_confirm_delete_"))
async def confirm_delete(callback: CallbackQuery):
    user_id = int(callback.data.rsplit("_", 1)[1])
    kb = admin_confirm_kb(user_id)
    await callback.message.edit_text(
        f"❗ Rostdan ham <b>{user_id}</b> adminligini olib tashlamoqchimisiz?",
        reply_markup=kb,
        parse_mode="HTML"
    )
@router.callback_query(AdminFilter(), F.data == "admin_back_to_list")
async def back_to_admin_list(callback: CallbackQuery):
    markup = await inline_admin_list_keyboard()
    await callback.message.edit_text(
        text="📋 Adminlar ro‘yxati:",
        reply_markup=markup
    )
@router.callback_query(AdminFilter(), F.data.startswith("admin_delete_"))
async def delete_admin(callback: CallbackQuery):
    user_id = int(callback.data.rsplit("_", 1)[1])
    updated = await update_user(user_id, is_admin=False)
    if updated:
        await callback.message.edit_text(f"✅ Admin <b>{user_id}</b> muvaffaqiyatli olib tashlandi.", parse_mode="HTML")
    else:
        await callback.message.answer("❌ Yangilashda xatolik yuz berdi.")
    markup = await inline_admin_list_keyboard()
    await callback.message.answer("📋 Yangilangan adminlar ro‘yxati:", reply_markup=markup)