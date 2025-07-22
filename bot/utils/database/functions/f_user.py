from datetime import datetime
from typing import List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from bot.data.config import toshkent_now
from bot.utils.database.models import User, engine, async_session

async def create_user(
    user_id: int,
    fullname: str = None,
    username: str = None,
    phone: str = None,
    language: str = None,
    is_blocked: bool = False,
    is_premium: bool = False,
    is_admin: bool = False,
    referral_id: int = None,
) -> User:
    async with AsyncSession(engine) as session:
        async with session.begin():
            try:
                new_user = User(
                    user_id=user_id,
                    fullname=fullname,
                    username=username,
                    phone=phone,
                    language=language,
                    is_blocked=is_blocked,
                    is_premium=is_premium,
                    is_admin=is_admin,
                    referral_id=referral_id,
                    created_at=toshkent_now(),
                    updated_at=toshkent_now()
                )
                session.add(new_user)
                await session.flush()
                await session.refresh(new_user)
                return new_user
            except SQLAlchemyError as e:
                await session.rollback()
                print(f"Xatolik: {e}")
                raise e


# ✅ 2. user_id orqali foydalanuvchini olish
async def get_user_by_user_id(user_id: int) -> User | None:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(User).where(User.user_id == user_id, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()


# ✅ 3. Foydalanuvchini yangilash
async def update_user(user_id: int, **kwargs) -> User | None:
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            user.updated_at = toshkent_now()
            await session.commit()
            return user
        return None

async def update_user_admin(user_id: int, is_admin: bool = True) -> bool:
    """
    user_id bo'yicha userni topib, is_admin ustunini yangilaydi.
    Muvaffaqiyatli bo'lsa True, aks holda False qaytaradi.
    """
    async with AsyncSession(engine) as session:
        try:
            result = await session.execute(
                select(User).where(User.user_id == user_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                return False

            user.is_admin = is_admin
            user.updated_at = toshkent_now()

            await session.commit()
            return True

        except SQLAlchemyError as e:
            await session.rollback()
            # logger.error(f"update_user_admin error: {e}")
            return False


# ✅ 4. Foydalanuvchini o‘chirish (soft delete)
async def delete_user_by_user_id(user_id: int) -> bool:
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.deleted_at = toshkent_now()
            await session.commit()
            return True
        return False


# ✅ 5. Foydalanuvchi mavjudligini tekshirish
async def user_exists(user_id: int) -> tuple[bool, User | None]:
    user = await get_user_by_user_id(user_id)
    return (True, user) if user else (False, None)


# ✅ 6. Barcha foydalanuvchilarni olish
async def get_all_users() -> List[User]:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(User).where(User.deleted_at.is_(None))
        )
        return list(result.scalars().all())

async def select_user_language(user_id: int):
    async with AsyncSession(engine) as session:
        if not user_id:
            return None
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        if user is not None:
            return user.language
        return user

async def count_users() -> int:
    async with async_session() as session:
        result = await session.execute(
            select(func.count()).select_from(User).where(User.deleted_at.is_(None))
        )
        return result.scalar_one()
async def count_active_users() -> int:
    async with async_session() as session:
        result = await session.execute(
            select(func.count()).select_from(User).where(
                User.is_blocked == False,
                User.deleted_at.is_(None)
            )
        )
        return result.scalar_one()

async def get_daily_users_count(date_str: str) -> int:
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    async with async_session() as session:
        stmt = (
            select(func.count())
            .select_from(User)
            .where(
                func.date(User.created_at) == date,
                User.deleted_at.is_(None)  # ✅ SQLAlchemy-style
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one()


async def get_daily_updated_users_count(date_str: str) -> int:
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    async with async_session() as session:
        stmt = (
            select(func.count())
            .select_from(User)
            .where(
                func.date(User.updated_at) == date,
                User.deleted_at.is_(None)  # ✅ SQLAlchemy-style
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one()

async def get_premium_users_count() -> int:
    async with async_session() as session:
        result = await session.execute(
            select(func.count()).select_from(User).where(
                User.is_premium == True,
                User.deleted_at.is_(None)
            )
        )
        return result.scalar_one()

async def get_all_admin_users() -> list[User]:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.is_admin == True)
        )
        return result.scalars().all()
async def get_user_byid(user_id: int) -> User | None:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()