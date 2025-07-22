from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from bot.data.texts import text

router = Router()

@router.callback_query(F.data.in_(["user_back", "user_check_subs"]))
async def handler_user_back(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    print(1)
    try:
        await callback_query.message.delete()
    except Exception as ex:
        print("handler_user_back error:", ex)

    await callback_query.message.answer(
        text("user_start"),
        reply_markup=ReplyKeyboardRemove()
    )
