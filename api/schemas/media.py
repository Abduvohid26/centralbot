from typing import List

from pydantic import BaseModel, Field
# Agar markaziy botda ham mavjud bo'lmasa keyin mana shunday qilib apidan yuklab olib bazasiga saqlash kerak va shunday qilib yuborish kerak markaziy botga
class MediaRequest(BaseModel):
    userbot_id: str = Field(..., description="User bot Telegram ID si")
    external_link: str = Field(..., description="Foydalanuvchidan kelgan link")
    external_bot_username: str = Field(..., description="A bot username (A botda so'ralgan malumot mavjud emas)")

class ExternalOnlyRequest(BaseModel):
    external_link: str = Field(..., description="Foydalanuvchidan kelgan link")
    external_bot_username: str = Field(..., description="userga malumot topib bera olmagan bot username")

class BotUsername(BaseModel):
    bot_username: str = Field(..., description="Yangi ochilgan bot username")

class AudioTextRequest(BaseModel):
    audio_text: str = Field(..., description="audio matni")
    external_bot_username: str = Field(..., description="musiqa topib beruvchi bot username")
