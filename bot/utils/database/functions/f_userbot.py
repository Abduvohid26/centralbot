from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from bot.utils.database.models import engine, UserBot
from sqlalchemy import select, func

# ✅ 1. UserBot yaratish
async def save_user_bot_to_db(
    phone: str,
    session_string: str,
    telegram_user_id: int,
    telegram_app_id: int
) -> UserBot:
    async with AsyncSession(engine) as session:
        async with session.begin():
            try:
                bot = UserBot(
                    phone_number=phone,
                    session_string=session_string,
                    telegram_user_id=telegram_user_id,
                    app_id=telegram_app_id
                )
                session.add(bot)
                await session.flush()
                await session.refresh(bot)
                return bot
            except SQLAlchemyError as e:
                await session.rollback()
                print(f"❌ Xatolik: {e}")
                raise e
# ✅ 2. Barcha UserBotlar
async def get_all_userbots() -> list[UserBot]:
    async with AsyncSession(engine) as session:
        result = await session.execute(select(UserBot))
        return result.scalars().all()

# ✅ 3. Telefon bo‘yicha olish
async def get_userbot_by_phone(phone_number: str) -> UserBot | None:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(UserBot).where(UserBot.phone_number == phone_number)
        )
        return result.scalar_one_or_none()

# ✅ 4. Yangilash
async def update_userbot(phone_number: str, **kwargs) -> UserBot | None:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(UserBot).where(UserBot.phone_number == phone_number)
        )
        bot = result.scalar_one_or_none()
        if bot:
            for key, value in kwargs.items():
                if hasattr(bot, key):
                    setattr(bot, key, value)
            await session.commit()
            return bot
        return None

# ✅ 5. O‘chirish
async def delete_userbot(phone_number: str) -> bool:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(UserBot).where(UserBot.phone_number == phone_number)
        )
        bot = result.scalar_one_or_none()
        if bot:
            await session.delete(bot)
            await session.commit()
            return True
        return False
# async def get_all_user_bots() -> list[UserBot]:
#     async with AsyncSession(engine) as session:
#         result = await session.execute(select(UserBot))
#         return result.scalars().all()


async def delete_userbot_by_id(bot_id: int) -> bool:
    async with AsyncSession(engine) as session:
        try:
            # Bot mavjudligini tekshirish
            result = await session.execute(
                select(UserBot).where(UserBot.id == bot_id)
            )
            bot = result.scalar_one_or_none()

            if not bot:
                return False

            await session.delete(bot)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            print(f"❌ delete_userbot_by_id error: {e}")
            return False

async def get_random_active_userbot() -> UserBot | None:
    async with AsyncSession(engine) as session:
        try:
            result = await session.execute(
                select(UserBot)
                .options(joinedload(UserBot.app))
                .where(UserBot.is_active == True)
                .order_by(func.random())
                .limit(1)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            await session.rollback()
            print(f"❌ get_random_active_userbot error: {e}")
            return None
async def get_userbot_by_telegram_id(telegram_user_id: int) -> UserBot | None:
    async with AsyncSession(engine) as session:
        try:
            result = await session.execute(
                select(UserBot)
                .options(joinedload(UserBot.app))
                .where(UserBot.telegram_user_id == telegram_user_id, UserBot.is_active == True)
                .limit(1)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            await session.rollback()
            print(f"❌ get_userbot_by_telegram_id error: {e}")
            return None

async def get_all_user_bots() -> list[UserBot]:
    async with AsyncSession(engine) as session:
        try:
            result = await session.execute(
                select(UserBot)
                .options(joinedload(UserBot.app))  # 🔥 bu yerda App bilan birga yuklanadi
                .where(UserBot.is_active == True)
            )
            return list(result.scalars().all())
        except Exception as e:
            await session.rollback()
            print(f"❌ get_all_user_bots error: {e}")
            return []