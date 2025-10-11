import os
import json
import random

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from core.models import GenerationRequest
from core.engine import DataGenerationEngine
from core.validators import validate_rules, validate_one_to_many
from . import GENERATED_DIR

router = APIRouter()


@router.post("/generate")
async def generate(req: GenerationRequest):
    try:
        blueprint = req.blueprint
        validate_rules(blueprint)
        validate_one_to_many(blueprint)
        engine = DataGenerationEngine(seed=req.seed)
        data = engine.execute(blueprint)

        filename = f"blueprint_{f'{random.randint(1000000, 9000000)}'}.json"
        filepath = os.path.join(GENERATED_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        download_url = f"/api/download/{filename}"
        return {
            "status": "success",
            "data": data,
            'download_url': download_url
            }
    except Exception as e:
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


@router.get("/download/{filename}")
async def download_file(filename: str):
    filepath = os.path.join(GENERATED_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Файл не найден")

    return FileResponse(
        filepath,
        media_type="application/json",
        filename=filename
    )
