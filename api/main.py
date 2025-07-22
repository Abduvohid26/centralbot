# api/main.py

from fastapi import FastAPI
from api.routes.media import router as media_router

app = FastAPI(
    title="Media API",
    version="1.0.0",
    docs_url="/docs",          # Swagger
    redoc_url="/redoc",        # ReDoc
)

# Marshrutlarni ulash
app.include_router(
    media_router,
    prefix="/api",             # Barcha endpointlar /api/... bo‘ladi
    tags=["Media"],            # Swagger'da ko‘rsatiladigan guruh nomi
)
