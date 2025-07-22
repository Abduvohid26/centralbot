import random
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from bot.utils.database.models import DB_bots, engine

# ✅ 1. Yangi bot qo‘shish
async def create_bot(username: str) -> DB_bots:
    async with AsyncSession(engine) as session:
        async with session.begin():
            try:
                new_bot = DB_bots(username=username)
                session.add(new_bot)
                await session.flush()
                await session.refresh(new_bot)
                return new_bot
            except SQLAlchemyError as e:
                await session.rollback()
                print(f"Xatolik (create_bot): {e}")
                raise e

# ✅ 2. Botni username orqali olish
async def get_bot_by_username(username: str) -> Optional[DB_bots]:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(DB_bots).where(DB_bots.username == username)
        )
        return result.scalar_one_or_none()

# ✅ 3. Botni id orqali olish
async def get_bot_by_id(bot_id: int) -> Optional[DB_bots]:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(DB_bots).where(DB_bots.id == bot_id)
        )
        return result.scalar_one_or_none()

# ✅ 4. Barcha botlarni olish
async def get_all_bots() -> List[DB_bots]:
    async with AsyncSession(engine) as session:
        result = await session.execute(select(DB_bots))
        return list(result.scalars().all())

# ✅ 5. Botni yangilash
async def update_bot_username(old_username: str, new_username: str) -> bool:
    async with AsyncSession(engine) as session:
        try:
            result = await session.execute(
                select(DB_bots).where(DB_bots.username == old_username)
            )
            bot = result.scalar_one_or_none()
            if not bot:
                return False

            bot.username = new_username
            await session.commit()
            return True
        except SQLAlchemyError as e:
            await session.rollback()
            print(f"Xatolik (update_bot_username): {e}")
            return False


# ✅ 6. Botni o‘chirish

async def delete_bot_by_username(username: str) -> bool:
    async with AsyncSession(engine) as session:
        try:
            await session.execute(
                delete(DB_bots).where(DB_bots.username == username)
            )
            await session.commit()
            return True
        except SQLAlchemyError as e:
            await session.rollback()
            print(f"❌ delete_bot_by_username xatolik: {e}")
            return False
async def get_all_bot_usernames() -> list[str]:
    async with AsyncSession(engine) as session:
        result = await session.execute(select(DB_bots.username))
        usernames = result.scalars().all()
        return list(usernames)
async def get_random_bot_username() -> Optional[str]:
    async with AsyncSession(engine) as session:
        try:
            result = await session.execute(select(DB_bots.username))
            usernames = result.scalars().all()
            if not usernames:
                return None
            return random.choice(usernames)
        except SQLAlchemyError as e:
            print(f"❌ get_random_bot_username xatolik: {e}")
            return None