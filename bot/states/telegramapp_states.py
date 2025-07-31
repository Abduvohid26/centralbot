from aiogram.fsm.state import State, StatesGroup

class AddTelegramAppFSM(StatesGroup):
    name = State()
    api_id = State()
    api_hash = State()

class AddTelegramAppFSMExtra(StatesGroup):
    name = State()
    api_id = State()
    api_hash = State()


class EditTelegramAppFSM(StatesGroup):
    name = State()
    api_id = State()
    api_hash = State()



class EditTelegramAppFSMExtra(StatesGroup):
    name = State()
    api_id = State()
    api_hash = State()