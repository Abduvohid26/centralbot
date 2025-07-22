# import asyncio
# import csv
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker
# from bot.utils.database.models import Media
#
# DATABASE_URL = "postgresql+asyncpg://postgres:123@db:5432/markaziy_bot"
#
# engine = create_async_engine(DATABASE_URL, echo=True)
# AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
#
# async def import_csv(file_path: str):
#     async with AsyncSessionLocal() as session:
#         media_objects = []
#         with open(file_path, newline='', encoding='utf-8') as csvfile:
#             reader = csv.DictReader(csvfile)
#             for row in reader:
#                 media = Media(
#                     platform="track",
#                     link=row.get("link"),
#                     file_id=row.get("file_id"),
#                     bot_username=row.get("bot_username"),
#                     bot_token=row.get("bot_token"),
#                     caption=None,
#                     channel_message_id=None,
#                     channel_id=None
#                 )
#                 media_objects.append(media)
#
#         session.add_all(media_objects)
#         await session.commit()
#
#     print("✅ CSV import muvaffaqiyatli yakunlandi")
#
# if __name__ == "__main__":
#     asyncio.run(import_csv("redis_track.csv"))
