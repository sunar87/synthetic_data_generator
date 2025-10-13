from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter()


@router.get("/download/{filename}")
def download_file(filename: str):
    """
    Возвращает сгенерированный JSON файл по имени.
    """
    path = os.path.join("generated", filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(path, filename=filename, media_type="application/json")
