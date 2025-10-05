from fastapi import APIRouter, HTTPException
from core.models import GenerationRequest
from core.engine import DataGenerationEngine
from core.validators import validate_rules

router = APIRouter()


@router.post("/generate")
async def generate(req: GenerationRequest):
    try:
        blueprint = req.blueprint
        validate_rules(blueprint)
        engine = DataGenerationEngine(seed=req.seed)
        data = engine.execute(blueprint)
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/validate")
async def validate(req: GenerationRequest):
    try:
        blueprint = req.blueprint
        validate_rules(blueprint)
        return {"status": "valid", "message": "Blueprint is valid"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
