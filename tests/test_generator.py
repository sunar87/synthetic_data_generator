import pytest
from fastapi.testclient import TestClient
from core.engine import DataGenerationEngine
from core.models import Blueprint, EntityDefinition, FieldDefinition, FieldType
from core.validators import validate_rules, validate_one_to_many
from api.routes import router
from api.main import app


client = TestClient(app)


# ---------- 1. UNIT TESTS ДЛЯ ЯДРА ---------- #

def make_blueprint_simple():
    """Простая схема без связей."""
    return Blueprint(
        entities={
            "users": EntityDefinition(
                count=3,
                fields={
                    "id": FieldDefinition(type=FieldType.INTEGER, params={}),
                    "name": FieldDefinition(type=FieldType.STRING, params={"subtype": "name"})
                },
            )
        }
    )


def make_blueprint_with_reference():
    """Blueprint с reference связью."""
    return Blueprint(
        entities={
            "users": EntityDefinition(
                count=2,
                fields={"id": FieldDefinition(type=FieldType.INTEGER, params={})},
            ),
            "orders": EntityDefinition(
                count=4,
                fields={
                    "id": FieldDefinition(type=FieldType.INTEGER, params={}),
                    "user_id": FieldDefinition(
                        type=FieldType.REFERENCE,
                        params={"entity": "users", "field": "id"}
                    )
                }
            ),
        }
    )


def make_blueprint_with_one_to_many():
    """Blueprint с one_to_many."""
    return Blueprint(
        entities={
            "users": EntityDefinition(
                count=2,
                fields={
                    "id": FieldDefinition(type=FieldType.INTEGER, params={}),
                    "orders": FieldDefinition(
                        type=FieldType.ONE_TO_MANY,
                        params={
                            "entity": "orders",
                            "foreign_field": "user_id",
                            "embed": True
                        }
                    ),
                }
            ),
            "orders": EntityDefinition(
                count=4,
                fields={
                    "id": FieldDefinition(type=FieldType.INTEGER, params={}),
                    "user_id": FieldDefinition(
                        type=FieldType.REFERENCE,
                        params={"entity": "users", "field": "id"}
                    ),
                }
            )
        }
    )


def test_simple_generation():
    bp = make_blueprint_simple()
    engine = DataGenerationEngine(seed=42)
    result = engine.execute(bp)
    assert "users" in result
    assert len(result["users"]) == 3
    assert all("id" in u and "name" in u for u in result["users"])


def test_reference_generation():
    bp = make_blueprint_with_reference()
    engine = DataGenerationEngine(seed=42)
    result = engine.execute(bp)
    orders = result["orders"]
    users = {u["id"] for u in result["users"]}
    assert all(o["user_id"] in users for o in orders)


def test_one_to_many_generation():
    bp = make_blueprint_with_one_to_many()
    engine = DataGenerationEngine(seed=42)
    result = engine.execute(bp)
    users = result["users"]
    assert "orders" in users[0]
    assert isinstance(users[0]["orders"], list)


# ---------- 2. VALIDATORS ---------- #

def test_validate_rules_no_error():
    bp = make_blueprint_simple()
    validate_rules(bp)  # должен пройти без исключений


def test_validate_one_to_many_no_error():
    bp = make_blueprint_with_one_to_many()
    validate_one_to_many(bp)  # должен пройти без ошибок


def test_validate_one_to_many_invalid():
    bp = make_blueprint_with_one_to_many()
    # намеренно портим foreign_field
    bp.entities["users"].fields["orders"].params["foreign_field"] = "nonexistent"
    with pytest.raises(ValueError):
        validate_one_to_many(bp)


# ---------- 3. RULES ---------- #

def test_rules_applied_correctly():
    from core.utils import match_condition, apply_action
    from faker import Faker

    faker = Faker()
    context = {
        "users": [{"id": 1, "is_vip": True}],
    }
    entity_data = {"user_id": 1, "price": 100}

    cond = {
        "entity": "users",
        "local_field": "user_id",
        "field": "is_vip",
        "op": "eq",
        "value": True
    }

    act = {
        "action": "set",
        "field": "price",
        "min": 1000,
        "max": 1200
    }

    assert match_condition(entity_data, context, cond)
    apply_action(entity_data, faker, act)
    assert 1000 <= entity_data["price"] <= 1200


# ---------- 4. API ТЕСТЫ ---------- #

def test_api_generate_basic():
    response = client.post("/api/generate", json={
        "seed": 42,
        "blueprint": {
            "entities": {
                "users": {
                    "count": 2,
                    "fields": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"}
                    }
                }
            }
        }
    })
    assert response.status_code == 200
    data = response.json()
    assert "users" in data["data"]


def test_api_generate_with_reference_and_one_to_many():
    payload = {
        "seed": 42,
        "blueprint": {
            "entities": {
                "users": {
                    "count": 2,
                    "fields": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "orders": {
                            "type": "one_to_many",
                            "params": {
                                "entity": "orders",
                                "foreign_field": "user_id",
                                "embed": True
                            }
                        }
                    }
                },
                "orders": {
                    "count": 4,
                    "fields": {
                        "id": {"type": "integer"},
                        "product": {"type": "string"},
                        "user_id": {
                            "type": "reference",
                            "params": {"entity": "users", "field": "id"}
                        }
                    }
                }
            }
        }
    }

    response = client.post("/api/generate", json=payload)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["users"]) == 2
    assert "orders" in data["users"][0]


def test_api_validate_endpoint():
    response = client.post("/api/validate", json={
        "seed": 123,
        "blueprint": {
            "entities": {
                "users": {
                    "count": 1,
                    "fields": {"id": {"type": "integer"}}
                }
            }
        }
    })
    assert response.status_code == 200
    assert response.json()["status"] == "valid"


def test_default_endpoint():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json()['message'] == 'API is running!'
