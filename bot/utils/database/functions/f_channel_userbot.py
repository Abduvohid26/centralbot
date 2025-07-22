import random
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from bot.utils.database.models import Channel_userbots, engine
from sqlalchemy.ext.asyncio import AsyncSession

async def create_channel_userbot(channel_chat_id: int, channel_name: str) -> Channel_userbots:
    async with AsyncSession(engine) as session:
        async with session.begin():
            try:
                new_channel = Channel_userbots(
                    channel_chat_id=channel_chat_id,
                    channel_name=channel_name
                )
                session.add(new_channel)
                await session.flush()
                await session.refresh(new_channel)
                return new_channel
            except SQLAlchemyError as e:
                await session.rollback()
                print(f"Xatolik: {e}")
                raise e

async def get_channel_by_chat_id(channel_chat_id: int) -> Channel_userbots | None:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(Channel_userbots).where(Channel_userbots.channel_chat_id == channel_chat_id)
        )
        return result.scalar_one_or_none()
async def get_channel_by_name(channel_name: str) -> Channel_userbots | None:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(Channel_userbots).where(Channel_userbots.channel_name == channel_name)
        )
        return result.scalar_one_or_none()
async def update_channel_userbot(channel_chat_id: int, **kwargs) -> Channel_userbots | None:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(Channel_userbots).where(Channel_userbots.channel_chat_id == channel_chat_id)
        )
        channel = result.scalar_one_or_none()
        if channel:
            # new_chat_id degan alohida param bilan update qilish
            if 'new_chat_id' in kwargs:
                channel.channel_chat_id = kwargs['new_chat_id']
            for key, value in kwargs.items():
                if key == 'new_chat_id':
                    continue  # yuqorida allaqachon update qildik
                if hasattr(channel, key):
                    setattr(channel, key, value)
            await session.commit()
            return channel
        return None

async def delete_channel_by_chat_id(channel_chat_id: int) -> bool:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(Channel_userbots).where(Channel_userbots.channel_chat_id == channel_chat_id)
        )
        channel = result.scalar_one_or_none()
        if channel:
            await session.delete(channel)
            await session.commit()
            return True
        return False

async def get_all_channels() -> list[Channel_userbots]:
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Channel_userbots))
        return list(result.scalars().all())

async def channel_exists(channel_chat_id: int) -> tuple[bool, Channel_userbots | None]:
    channel = await get_channel_by_chat_id(channel_chat_id)
    return (True, channel) if channel else (False, None)
from sqlalchemy import func

async def count_channels() -> int:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(func.count()).select_from(Channel_userbots)
        )
        return result.scalar_one()

async def get_random_channel_id() -> int | None:
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Channel_userbots.channel_chat_id))
        channel_ids = [row[0] for row in result.all()]
        if not channel_ids:
            return None
        return random.choice(channel_ids)