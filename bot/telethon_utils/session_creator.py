from telethon.sync import TelegramClient
from telethon.sessions import StringSession

async def get_session_string(phone: str, code: str, code_hash: str, app_id: int, app_hash: str, password: str = None):
    client = TelegramClient(StringSession(), app_id, app_hash)
    await client.connect()

    try:
        if password:
            await client.sign_in(password=password)
        else:
            await client.sign_in(phone=phone, code=code, phone_code_hash=code_hash)

        session_str = client.session.save()
        me = await client.get_me()
        return session_str, me.id

    finally:
        await client.disconnect()