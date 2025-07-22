from .start import router as start_router
from .dispatch import router as dispatch_router
from .service_bot import router as service_bot_router

routers = [start_router, dispatch_router, service_bot_router]
