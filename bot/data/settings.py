from sqlalchemy import select
from bot.data.config import OWNER_ID
from bot.utils.database.models import async_session
from bot.utils.database.models import User
print("999999999999")

async def load_settings():
    async with async_session() as session:
        # Bazadagi admin user_id larini olish
        result = await session.execute(
            select(User.user_id).where(User.is_admin == True)
        )
        db_admins = [row[0] for row in result.all()]
        # OWNER_ID ni ham qo‘shib, takrorlanmaydigan list yasash
        admins = list(set(db_admins + [OWNER_ID]))
        return admins