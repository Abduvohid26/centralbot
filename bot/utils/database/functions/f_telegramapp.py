from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from bot.utils.database.models import TelegramApp, engine, TelegramAppExtra


# ✅ 1. TelegramApp yaratish
async def create_telegram_app(name: str, api_id: int, api_hash: str) -> TelegramApp:
    async with AsyncSession(engine) as session:
        async with session.begin():
            try:
                app = TelegramApp(name=name, api_id=api_id, api_hash=api_hash)
                session.add(app)
                await session.flush()
                await session.refresh(app)
                return app
            except SQLAlchemyError as e:
                await session.rollback()
                print(f"Xatolik: {e}")
                raise e


async def create_telegram_app_extra(name: str, api_id: int, api_hash: str) -> TelegramAppExtra:
    async with AsyncSession(engine) as session:
        async with session.begin():
            try:
                app = TelegramAppExtra(name=name, api_id=api_id, api_hash=api_hash)
                session.add(app)
                await session.flush()
                await session.refresh(app)
                return app
            except SQLAlchemyError as e:
                await session.rollback()
                print(f"Xatolik: {e}")
                raise e

# ✅ 2. Barcha TelegramApp larni olish
async def get_all_telegram_apps() -> list[TelegramApp]:
    async with AsyncSession(engine) as session:
        result = await session.execute(select(TelegramApp))
        return result.scalars().all()


# ✅ 2. Barcha TeTelegramAppExtra larni olish 
async def get_all_telegram_apps_extra() -> list[TelegramAppExtra]:
    async with AsyncSession(engine) as session:
        result = await session.execute(select(TelegramAppExtra))
        return result.scalars().all()


# ✅ 3. ID bo‘yicha olish
async def get_telegram_app_by_id(app_id: int) -> TelegramApp | None:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(TelegramApp).where(TelegramApp.id == app_id)
        )
        return result.scalar_one_or_none()


async def get_telegram_app_by_id_extra(app_id: int) -> TelegramAppExtra | None:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(TelegramAppExtra).where(TelegramAppExtra.id == app_id)
        )
        return result.scalar_one_or_none()

# ✅ 4. TelegramApp yangilash
async def update_telegram_app(app_id: int, **kwargs) -> TelegramApp | None:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(TelegramApp).where(TelegramApp.id == app_id)
        )
        app = result.scalar_one_or_none()
        if app:
            for key, value in kwargs.items():
                if hasattr(app, key):
                    setattr(app, key, value)
            await session.commit()
            return app
        return None
    
async def update_telegram_app_extra(app_id: int, **kwargs) -> TelegramAppExtra | None:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(TelegramAppExtra).where(TelegramAppExtra.id == app_id)
        )
        app = result.scalar_one_or_none()
        if app:
            for key, value in kwargs.items():
                if hasattr(app, key):
                    setattr(app, key, value)
            await session.commit()
            return app
        return None

# ✅ 5. O‘chirish
async def delete_telegram_app(app_id: int) -> bool:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(TelegramApp).where(TelegramApp.id == app_id)
        )
        app = result.scalar_one_or_none()
        if app:
            await session.delete(app)
            await session.commit()
            return True
        return False

async def delete_telegram_app_by_id(app_id: int) -> bool:
    async with AsyncSession(engine) as session:
        result = await session.execute(select(TelegramApp).where(TelegramApp.id == app_id))
        app = result.scalar_one_or_none()
        if app:
            await session.delete(app)
            await session.commit()
            return True
        return False
    

async def delete_telegram_app_by_id_extra(app_id: int) -> bool:
    async with AsyncSession(engine) as session:
        result = await session.execute(select(TelegramAppExtra).where(TelegramAppExtra.id == app_id))
        app = result.scalar_one_or_none()
        if app:
            await session.delete(app)
            await session.commit()
            return True
        return False
    

async def get_telegram_app_by_name(name: str) -> TelegramApp | None:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(TelegramApp).where(TelegramApp.name == name)
        )
        return result.scalar_one_or_none()
    
async def get_telegram_app_by_name_extra(name: str) -> TelegramAppExtra | None:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(TelegramAppExtra).where(TelegramAppExtra.name == name)
        )
        return result.scalar_one_or_none()


async def available_telegram_apps():
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(TelegramApp).options(selectinload(TelegramApp.user_bots))
        )
        apps = result.scalars().all()
        return [app for app in apps if len(app.user_bots) < 10]
    

async def available_telegram_apps_extra():
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(TelegramAppExtra).options(selectinload(TelegramAppExtra.user_bots))
        )
        apps = result.scalars().all()
        return [app for app in apps if len(app.user_bots) < 10]