import json
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


@pytest.fixture
def simple_blueprint():
    """Минимальный корректный blueprint"""
    return {
        "blueprint": {
            "entities": {
                "users": {
                    "count": 3,
                    "fields": {
                        "id": {"type": "integer"},
                        "name": {"type": "string", "params": {"min_length": 3, "max_length": 12}},
                        "is_vip": {"type": "boolean"}
                    }
                }
            }
        },
        "seed": 123
    }


# --- /api/health -----------------------------------------------------------

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# --- /api/generate ---------------------------------------------------------

def test_generate_success(simple_blueprint):
    """Проверяем успешную генерацию"""
    response = client.post("/api/generate", json=simple_blueprint)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert "download_url" in data


def test_generate_invalid_request():
    """Проверяем, что при некорректных данных возвращается 422"""
    bad_json = {"invalid": "data"}
    response = client.post("/api/generate", json=bad_json)
    assert response.status_code == 422


# --- /api/download/{filename} ---------------------------------------------

def test_download_existing_file(tmp_path, simple_blueprint, monkeypatch):
    """Проверяем успешную загрузку файла"""

    # Сначала сгенерируем данные
    response = client.post("/api/generate", json=simple_blueprint)
    assert response.status_code == 200
    download_url = response.json()["download_url"]
    assert download_url.startswith("/api/download/")

    # Теперь запрашиваем сам файл
    download_response = client.get(download_url)
    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == "application/json"

    # Проверяем, что контент читается как JSON
    json_data = json.loads(download_response.text)
    assert "users" in json_data


def test_download_nonexistent_file():
    """Запрос несуществующего файла должен вернуть 404"""
    response = client.get("/api/download/no_such_file.json")
    assert response.status_code == 404
