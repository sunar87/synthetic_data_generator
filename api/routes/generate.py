import os
import json
from uuid import uuid4
import time

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from core.engine import DataGenerationEngine
from core.models import GenerationRequest
from core.validators import validate_one_to_many, validate_rules
from api.loger import get_logger


router = APIRouter()
logger = get_logger(__name__)


@router.post("/generate", response_class=JSONResponse)
def generate_data(request: GenerationRequest):
    """
    Генерирует данные на основе переданного blueprint.
    Возвращает результат и ссылку для скачивания файла.
    """
    start_time = time.time()
    try:
        logger.info(f"Запрос на генерацию: seed={request.seed}, entities={list(request.blueprint.entities.keys())}")
        validate_one_to_many(request.blueprint)
        validate_rules(request.blueprint)

        engine = DataGenerationEngine(request.seed)
        data = engine.execute(request.blueprint)

        os.makedirs("generated", exist_ok=True)
        filename = f"blueprint_{uuid4().hex}.json"
        file_path = os.path.join("generated", filename)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return {
            "status": "success",
            "data": data,
            "download_url": f"/api/download/{filename}"
        }

    except Exception as e:
        elapsed = round(time.time() - start_time, 2)
        logger.exception(f"❌ Ошибка при генерации ({elapsed}s): {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/validate")
async def validate(req: GenerationRequest):
    try:
        blueprint = req.blueprint
        validate_rules(blueprint)
        validate_one_to_many(blueprint)
        return {"status": "valid", "message": "Blueprint is valid"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))