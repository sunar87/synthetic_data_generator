from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    """
    Проверка состояния API.
    """
    return {"status": "ok"}
