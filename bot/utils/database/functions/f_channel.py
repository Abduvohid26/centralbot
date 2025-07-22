from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from bot.utils.database.models import engine, Channel


# ✅ 1. Kanal yaratish
async def create_channel(chat_id: int, title: str) -> Channel:
    async with AsyncSession(engine) as session:
        async with session.begin():
            try:
                new_channel = Channel(
                    chat_id=chat_id,
                    title=title
                )
                session.add(new_channel)
                await session.flush()
                await session.refresh(new_channel)
                return new_channel
            except SQLAlchemyError as e:
                await session.rollback()
                print(f"Xatolik: {e}")
                raise e


# ✅ 2. Barcha kanallarni olish
async def get_all_channels() -> list[Channel]:
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Channel))
        return result.scalars().all()

# ✅ 3. Kanalni chat_id orqali olish
async def get_channel_by_chat_id(chat_id: int) -> Channel | None:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(Channel).where(Channel.chat_id == chat_id)
        )
        return result.scalar_one_or_none()


# ✅ 4. Kanalni yangilash
async def update_channel(chat_id: int, **kwargs) -> Channel | None:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(Channel).where(Channel.chat_id == chat_id)
        )
        channel = result.scalar_one_or_none()
        if channel:
            for key, value in kwargs.items():
                if hasattr(channel, key):
                    setattr(channel, key, value)
            await session.commit()
            return channel
        return None


# ✅ 5. Kanalni o‘chirish
async def delete_channel(chat_id: int) -> bool:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(Channel).where(Channel.chat_id == chat_id)
        )
        channel = result.scalar_one_or_none()
        if channel:
            await session.delete(channel)
            await session.commit()
            return True
        return False


# ✅ 6. Kanal mavjudligini tekshirish
async def channel_exists(chat_id: int) -> bool:
    channel = await get_channel_by_chat_id(chat_id)
    return channel is not None
