from aiogram.fsm.state import StatesGroup, State

class AddChannelState(StatesGroup):
    waiting_for_channel_name = State()
    waiting_for_channel_chat_id = State()

class EditChannelState(StatesGroup):
    waiting_for_channel_name = State()
    waiting_for_channel_chat_id = State()
