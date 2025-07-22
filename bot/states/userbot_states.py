from aiogram.fsm.state import State, StatesGroup

class AddUserBotFSM(StatesGroup):
    choose_app = State()
    phone = State()
    code = State()
    password = State()
