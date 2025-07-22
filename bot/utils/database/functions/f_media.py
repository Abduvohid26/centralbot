from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from bot.utils.database.models import engine, Media
import csv

# 1. Media yaratish
async def create_media(
    platform: str,
    link: str,
    file_id: str,
    caption: str = None,
    bot_username: str = None,
    bot_token: str = None,
    channel_message_id: str = None,
    channel_id: str = None,
) -> Media:
    async with AsyncSession(engine) as session:
        async with session.begin():
            try:
                new_media = Media(
                    platform=platform,
                    link=link,
                    file_id=file_id,
                    caption=caption,
                    bot_username=bot_username,
                    bot_token=bot_token,
                    channel_message_id=channel_message_id,
                    channel_id=channel_id
                )
                session.add(new_media)
                await session.flush()
                await session.refresh(new_media)
                return new_media
            except SQLAlchemyError as e:
                await session.rollback()
                print(f"❌ create_media xatolik: {e}")
                raise

# 2. Barcha media fayllarni olish
async def get_all_media() -> list[Media]:
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Media))
        return result.scalars().all()

# 3. Link orqali media topish
async def get_media_by_link(link: str) -> Media | None:
    async with AsyncSession(engine) as session:
        try:
            result = await session.execute(
                select(Media).where(Media.link == link)
            )
            media = result.scalars().first()
            return media
        except Exception as e:
            await session.rollback()
            print(f"❌ get_media_by_link xatolik: {link} 77777777777 {e}")
            return None


# 4. Media faylni yangilash
async def update_media(link: str, **kwargs) -> Media | None:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(Media).where(Media.link == link)
        )
        media = result.scalar_one_or_none()
        if media:
            for key, value in kwargs.items():
                if hasattr(media, key):
                    setattr(media, key, value)
            await session.commit()
            await session.refresh(media)
            return media
        return None

# 5. Media faylni o‘chirish
async def delete_media_by_link(link: str) -> bool:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(Media).where(Media.link == link)
        )
        media = result.scalar_one_or_none()
        if media:
            await session.delete(media)
            await session.commit()
            return True
        return False

# 6. Link mavjudligini tekshirish
async def media_exists(link: str) -> bool:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(Media.id).where(Media.link == link)
        )
        return result.scalar_one_or_none() is not None

# 7. Linkni tekshirish (shortcut)
async def check_media_link(link: str) -> bool:
    return await media_exists(link)

async def import_media_from_csv(file_path: str):
    async with AsyncSession(engine) as session:
        with open(file_path, mode="r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                media = Media(
                    link=row["link"],
                    file_id=row["file_id"],
                    bot_username=row.get("bot_username"),
                    bot_token=row.get("bot_token"),
                    # platform, caption, channel_id, channel_message_id NULL bo‘lib qoladi
                )
                session.add(media)
        await session.commit()
    print("9999999999999")