from fastapi import FastAPI
from api.routes import router

app = FastAPI(title="Synthetic Data Generator API")

app.include_router(router, prefix="/api", tags=["generation"])


@app.get("/")
def root():
    return {"message": "API is running!"}
