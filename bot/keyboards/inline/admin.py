from math import ceil

from aiogram.types import (
        InlineKeyboardMarkup as IKM,
        InlineKeyboardButton as IKB
    )
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.data.texts import button
from bot.utils.database.functions.f_dbbot import get_all_bot_usernames
from bot.utils.database.functions.f_telegramapp import get_all_telegram_apps, get_all_telegram_apps_extra
from bot.utils.database.functions.f_user import get_all_admin_users
from bot.utils.database.models import TelegramApp, Channel_userbots


def inline_admin_keyboards(*args):
    return [IKB(text=button("admin_back" if i.startswith("admin_back_extra") else i), callback_data=i) for i in args]

admin_main_menu = IKM(
    row_width=1,
    inline_keyboard=[
        inline_admin_keyboards("admin_send_message"),
        inline_admin_keyboards("admin_statistics"),
        inline_admin_keyboards("admin_admins"),
        inline_admin_keyboards("admin_telegramapp"),
        inline_admin_keyboards("admin_telegramapp_extra"),
        inline_admin_keyboards("admin_userbot"),
        inline_admin_keyboards("admin_userbot_extra"),
        inline_admin_keyboards("admin_link_statestika"),
        inline_admin_keyboards("admin_dbbots")
    ]
)

admin_back_menu = IKM(
    row_width=1,
    inline_keyboard=[
        inline_admin_keyboards("admin_back")
    ]
)

async def inline_telegramapp_list_keyboard() -> IKM:
    apps = await get_all_telegram_apps()
    builder = InlineKeyboardBuilder()

    # Har bir app uchun alohida tugma
    for app in apps:
        builder.row(
            IKB(
                text=app.name,
                callback_data=f"admin_view_telegramapp_{app.id}"
            )
        )
    builder.row(
        IKB(text="➕ APP qo‘shish", callback_data="admin_add_telegramapp"),
                IKB(text="⬅️ Ortga", callback_data="admin_back")
    )
    return builder.as_markup()




async def inline_telegramapp_list_keyboard_extra() -> IKM:
    apps = await get_all_telegram_apps_extra()
    print(apps, "apss")
    builder = InlineKeyboardBuilder()

    # Har bir app uchun alohida tugma
    for app in apps:
        print(app.id, "app")
        builder.row(
            IKB(
                text=app.name,
                callback_data=f"admin_extra_view_telegramapp_{app.id}"
            )
        )
    builder.row(
        IKB(text="➕ APP qo‘shish", callback_data="admin_add_telegramapp_extra"),
                IKB(text="⬅️ Ortga", callback_data="admin_back_extra")
    )
    return builder.as_markup()



app_menu_buttons = IKM(
        inline_keyboard=[
            [IKB(text="⬅️ Ortga", callback_data="admin_telegramapp")]
        ]
    )

app_menu_buttons_extra = IKM(
        inline_keyboard=[
            [IKB(text="⬅️ Ortga", callback_data="admin_telegramapp_extra")]
        ]
    )


apps_menu_buttons = IKM(
        inline_keyboard=[
            [IKB(text="⬅️ Ortga", callback_data="admin_add_telegramapp")]
        ]
    )

def telegramapp_info_buttons(app_id: int) -> IKM:
    return IKM(
        inline_keyboard=[
            [IKB(text="📱 Nomi", callback_data="admin_app_name"), IKB(text="🆔 API_ID", callback_data="admin_app_id")],
            [IKB(text="🔐 API_HASH", callback_data="admin_app_apihash")],
            [IKB(text="🗑 O‘chirish", callback_data=f"admin_delete_telegramapp_{app_id}"),
             IKB(text="⬅️ Ortga", callback_data="admin_telegramapp")]
        ]
    )


def telegramapp_info_buttons_extra(app_id: int) -> IKM:
    return IKM(
        inline_keyboard=[
            [IKB(text="📱 Nomi", callback_data="admin_app_extra_name"), IKB(text="🆔 API_ID", callback_data="admin_app_extra_id")],
            [IKB(text="🔐 API_HASH", callback_data="admin_app_extra_apihash")],
            [IKB(text="🗑 O‘chirish", callback_data=f"extra_confirm_delete_userbot_{app_id}"),
             IKB(text="⬅️ Ortga", callback_data="admin_telegramapp_extra")]
        ]
    )

def confirm_delete_telegramapp_buttons(app_id: int) -> IKM:
    return IKM(
        inline_keyboard=[
            [
                IKB(text="✅ Ha, o‘chirish", callback_data=f"confirm_delete_telegramapp_{app_id}"),
                IKB(text="❌ Bekor qilish", callback_data=f"admin_view_telegramapp_{app_id}")
            ]
        ]
    )

def confirm_delete_telegramapp_buttons_extra(app_id: int) -> IKM:
    return IKM(
        inline_keyboard=[
            [
                IKB(text="✅ Ha, o‘chirish", callback_data=f"extra_confirm_delete_telegramapp_{app_id}"),
                IKB(text="❌ Bekor qilish", callback_data=f"admin_extra_view_telegramapp_{app_id}")
            ]
        ]
    )

def back_admin_view(app_id: int) -> IKM:
    return IKM(
        inline_keyboard=[
            [IKB(text="⬅️ Ortga", callback_data=f"admin_view_telegramapp_{app_id}")]
        ]
    )

def back_admin_view_extra(app_id: int) -> IKM:
    return IKM(
        inline_keyboard=[
            [IKB(text="⬅️ Ortga", callback_data=f"admin_extra_view_telegramapp_{app_id}")]
        ]
    )


def inline_userbot_list_keyboard(bots: list, page: int = 1, per_page: int = 10) -> tuple[str, IKM]:
    if not bots:
        text = "❌ Bazada hech qanday user bot mavjud emas"
        kb = IKM(
            inline_keyboard=[
                [IKB(text="➕ Qo‘shish", callback_data="admin_add_userbot")],
                [IKB(text="⬅️ Ortga", callback_data="admin_back")]
            ]
        )
        return text, kb

    builder = InlineKeyboardBuilder()

    start = (page - 1) * per_page
    end = start + per_page
    page_bots = bots[start:end]

    row = []
    for bot in page_bots:
        row.append(IKB(
            text=f"{'🟡' if bot.is_active else '🔴'} {bot.phone_number}",
            callback_data=f"view_userbot_{bot.id}"
        ))
        if len(row) == 2:
            builder.row(*row)
            row = []
    if row:
        builder.row(*row)

    total_pages = ceil(len(bots) / per_page)
    if total_pages > 1:
        slider_buttons = []
        if page > 1:
            slider_buttons.append(IKB(text="⬅️ Oldingi", callback_data=f"userbot_page_{page-1}"))
        if page < total_pages:
            slider_buttons.append(IKB(text="Keyingi ➡️", callback_data=f"userbot_page_{page+1}"))
        builder.row(*slider_buttons)

    builder.row(
        IKB(text="➕ Qo‘shish", callback_data="admin_add_userbot"),
        IKB(text="⬅️ Ortga", callback_data="admin_back")
    )

    # Statistikani hisoblash
    total_count = len(bots)
    active_count = len([b for b in bots if b.is_active])
    blocked_count = total_count - active_count

    text = (
        "📱 <b>UserBot ro‘yxati:</b>\n\n"
        f"Jami: <b>{total_count}</b> ta\n\n"
        f"🟡 Faol: <b>{active_count}</b> ta\n\n"
        f"🔴 Bloklangan: <b>{blocked_count}</b> ta\n"
    )

    return text, builder.as_markup()



def inline_userbot_list_keyboard_extra(bots: list, page: int = 1, per_page: int = 10) -> tuple[str, IKM]:
    if not bots:
        text = "❌ Bazada hech qanday user bot mavjud emas"
        kb = IKM(
            inline_keyboard=[
                [IKB(text="➕ Qo‘shish", callback_data="admin_add_userbot_extra")],
                [IKB(text="⬅️ Ortga", callback_data="admin_back_extra")]
            ]
        )
        return text, kb

    builder = InlineKeyboardBuilder()

    start = (page - 1) * per_page
    end = start + per_page
    page_bots = bots[start:end]

    row = []
    for bot in page_bots:
        row.append(IKB(
            text=f"{'🟡' if bot.is_active else '🔴'} {bot.phone_number}",
            callback_data=f"extra_view_userbot_{bot.id}"
        ))
        if len(row) == 2:
            builder.row(*row)
            row = []
    if row:
        builder.row(*row)

    total_pages = ceil(len(bots) / per_page)
    if total_pages > 1:
        slider_buttons = []
        if page > 1:
            slider_buttons.append(IKB(text="⬅️ Oldingi", callback_data=f"userbot_extra_page_{page-1}"))
        if page < total_pages:
            slider_buttons.append(IKB(text="Keyingi ➡️", callback_data=f"userbot_extra_page_{page+1}"))
        builder.row(*slider_buttons)

    builder.row(
        IKB(text="➕ Qo‘shish", callback_data="admin_add_userbot_extra"),
        IKB(text="⬅️ Ortga", callback_data="admin_back_extra")
    )

    # Statistikani hisoblash
    total_count = len(bots)
    active_count = len([b for b in bots if b.is_active])
    blocked_count = total_count - active_count

    text = (
        "📱 <b>UserBot ro‘yxati:</b>\n\n"
        f"Jami: <b>{total_count}</b> ta\n\n"
        f"🟡 Faol: <b>{active_count}</b> ta\n\n"
        f"🔴 Bloklangan: <b>{blocked_count}</b> ta\n"
    )

    return text, builder.as_markup()


def choose_app_buttons(apps: list[TelegramApp]) -> IKM:
    kb = InlineKeyboardBuilder()
    for app in apps:
        kb.button(
            text=f"{app.name} ({len(app.user_bots)}/10)",
            callback_data=f"choose_app_{app.id}"
        )
    kb.adjust(1)
    return kb.as_markup()

def choose_app_buttons_extra(apps: list[TelegramApp]) -> IKM:
    kb = InlineKeyboardBuilder()
    for app in apps:
        kb.button(
            text=f"{app.name} ({len(app.user_bots)}/10)",
            callback_data=f"extra_choose_app_{app.id}"
        )
    kb.adjust(1)
    return kb.as_markup()

def confirm_delete_userbot_buttons(bot_id: int) -> IKM:
    return IKM(
        inline_keyboard=[
            [
                IKB(text="✅ Ha, o‘chirish", callback_data=f"confirm_delete_userbot_{bot_id}"),
                IKB(text="❌ Yo‘q", callback_data="cancel_delete_userbot")
            ]
        ]
    )

def confirm_delete_userbot_buttons_extra(bot_id: int) -> IKM:
    return IKM(
        inline_keyboard=[
            [
                IKB(text="✅ Ha, o‘chirish", callback_data=f"extra_confirm_delete_userbot_{bot_id}"),
                IKB(text="❌ Yo‘q", callback_data="_extra_cancel_delete_userbot_extra")
            ]
        ]
    )

def build_channels_inline_keyboard(channels: list) -> IKM:
    keyboard = []
    if channels:
        buttons = [
            IKB(text=ch.channel_name, callback_data=f"admin_channel_detail:{ch.channel_chat_id}")
            for ch in channels
        ]
        for i in range(0, len(buttons), 2):
            keyboard.append(buttons[i:i+2])

    keyboard.append([
        IKB(text="➕ Kanal qo‘shish", callback_data="admin_channel_userbot_add"),
        IKB(text="⬅️ Ortga", callback_data="admin_back"),
    ])
    return IKM(inline_keyboard=keyboard)

def build_channel_detail_keyboard(channel: Channel_userbots) -> IKM:
    return IKM(inline_keyboard=[
        [
            IKB(text=f"📢 Kanal nomi: {channel.channel_name}", callback_data=f"edit_channel_name:{channel.channel_chat_id}")
        ],
        [
            IKB(text=f"🆔 Chat ID: {channel.channel_chat_id}", callback_data=f"edit_channel_chat_id:{channel.channel_chat_id}")
        ],
        [
            IKB(text="❌ O‘chirish", callback_data=f"admin_channel_delete:{channel.channel_chat_id}"),
            IKB(text="⬅️ Ortga", callback_data="admin_channel_userbot_back"),
        ]
    ])

def build_channel_delete_confirm_keyboard(channel_chat_id: int) -> IKM:
    return IKM(inline_keyboard=[
        [
            IKB(text="✅ Ha, o‘chirish", callback_data=f"admin_channel_delete_confirm:{channel_chat_id}"),
            IKB(text="❌ Yo‘q", callback_data="admin_channel_userbot_back"),
        ]
    ])


async def inline_admin_list_keyboard() -> IKM:
    admins = await get_all_admin_users()
    builder = InlineKeyboardBuilder()
    for admin in admins:
        label = admin.fullname or admin.username or str(admin.user_id)
        builder.row(
            IKB(
                text=f"👤 {label}",
                callback_data=f"admin_view_user_{admin.user_id}"
            )
        )
    if not admins:
        builder.row(
            IKB(text="📭 Hozircha hech qanday admin mavjud emas.", callback_data="ignore")
        )
    builder.row(
        IKB(text="➕ Admin qo‘shish", callback_data="admin_add_admin"),
        IKB(text="⬅️ Ortga", callback_data="admin_back")
    )
    return builder.as_markup()

def admin_action_kb(user_id: int) -> IKM:
    builder = InlineKeyboardBuilder()
    builder.row(
        IKB(text="🗑️ O‘chirish", callback_data=f"admin_confirm_delete_{user_id}"),
        IKB(text="⬅️ Ortga", callback_data="admin_back_to_list")
    )
    return builder.as_markup()

def admin_confirm_kb(user_id: int) -> IKM:
    builder = InlineKeyboardBuilder()
    builder.row(
        IKB(text="✅ Ha", callback_data=f"admin_delete_{user_id}"),
        IKB(text="❌ Yo‘q", callback_data="admin_back_to_list")
    )
    return builder.as_markup()


async def generate_bot_list_keyboard():
    usernames = await get_all_bot_usernames()

    buttons = []
    if usernames:
        for username in usernames:
            buttons.append([IKB(text=username, callback_data=f"admin_db_bot_{username}")])
        text = "🧾 Botlar ro'yxati:"
    else:
        text = "❌ Hali botlar mavjud emas"

    # pastki tugmalar
    buttons.append([
        IKB(text="➕ Bot qo‘shish", callback_data="admin_add_bots"),
        IKB(text="🔙 Ortga", callback_data="admin_back")
    ])

    keyboard = IKM(inline_keyboard=buttons)
    return text, keyboard

def generate_single_bot_keyboard(username: str) -> IKM:
    return IKM(inline_keyboard=[
        [
            IKB(text="📝 Tahrirlash", callback_data=f"admindb_edit_bot_{username}"),
            IKB(text="❌ O‘chirish", callback_data=f"admindb_delete_bot_{username}")
        ],
        [
            IKB(text="🔙 Ortga", callback_data="admin_dbbots")
        ]
    ])

def generate_delete_confirm_keyboard(username: str) -> IKM:
    return IKM(inline_keyboard=[
        [
            IKB(text="✅ Ha", callback_data=f"admindb_confirm_delete_bot_{username}"),
            IKB(text="❌ Yo‘q", callback_data=f"admindb_cancel_delete_bot_{username}")
        ]
    ])


async def generate_back_button(callback_data: str) -> IKM:
    return IKM(inline_keyboard=[
        [IKB(text="🔙 Ortga", callback_data=callback_data)]
    ])