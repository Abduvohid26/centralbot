from aiogram.fsm.state import StatesGroup, State


class AddSimpleBotFSM(StatesGroup):
    waiting_for_username = State()

class EditBotFSM(StatesGroup):
    waiting_for_new_username = State()