from fastapi import FastAPI
from api.routes import generate, download, health

app = FastAPI(
    title="Synthetic Data Generator API",
    version="1.0.0",
    description="API для генерации синтетических данных по JSON-чертежу."
)

# Подключаем роутеры с сохранением адресов
app.include_router(generate.router, prefix="/api", tags=["Generate"])
app.include_router(download.router, prefix="/api", tags=["Download"])
app.include_router(health.router, prefix="/api", tags=["Health"])
