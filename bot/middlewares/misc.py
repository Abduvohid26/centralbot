from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.data.texts import button
from bot.utils.database.functions.f_channel import get_all_channels
from bot.utils.misc import subscription


async def check_status(user_id: int):
    final_status = True
    builder = InlineKeyboardBuilder()

    channels = await get_all_channels()  # 🔄 bazadan barcha kanallarni olish
    for channel in channels:
        try:
            status = await subscription.check(
                user_id=user_id,
                channel=channel.chat_id
            )
            final_status &= status
            if not status:
                builder.button(
                    text=channel.title,
                    url=f"https://t.me/{channel.title.replace(' ', '_')}"  # yoki channel.link bo‘lsa, shuni ishlat
                )
        except Exception as ex:
            print("check channels:", ex)

    # ⏳ "Tekshirish" tugmasi
    builder.button(
        text=button("user_check_subscribe"),
        callback_data="user_check_subs"
    )

    return final_status, builder.as_markup()
