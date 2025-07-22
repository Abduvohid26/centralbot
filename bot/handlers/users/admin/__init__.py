from .admin_base import router as admin_base_router
from .admin_users import router as admin_users_router
from .admin_telegramapp import router as admin_telegramapp_router
from .admin_userbot import router as admin_userbot_router
from .admin_stat_link import router as admin_stat_link_router
from .admin_channel_userbot import router as admin_channel_userbot_router
from .admin_admins import router as admin_admins_router
from .admin_db_botlar import router as admin_db_botlar_router
routers = [admin_base_router, admin_users_router,
           admin_telegramapp_router, admin_userbot_router,
           admin_stat_link_router, admin_channel_userbot_router,
           admin_admins_router, admin_db_botlar_router]

