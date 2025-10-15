import pytest
from pydantic import ValidationError
from core.models import (
    FieldDefinition, FieldType, Blueprint, EntityDefinition,
    Condition, Action, Rule, GenerationRequest
)


def test_fielddefinition_valid_params():
    fd = FieldDefinition(type=FieldType.STRING, params={"min_length": 3, "max_length": 10})
    assert fd.params["min_length"] == 3


def test_fielddefinition_invalid_params():
    with pytest.raises(ValueError, match="Недопустимые параметры"):
        FieldDefinition(type=FieldType.STRING, params={"invalid": 123})


def test_reference_requires_entity_and_field():
    with pytest.raises(ValueError, match="обязательны параметры"):
        FieldDefinition(type=FieldType.REFERENCE, params={"entity": "users"})


def test_entitydefinition_requires_fields():
    with pytest.raises(ValidationError, match="хотя бы одно поле"):
        EntityDefinition(count=1, fields={})


def test_entitydefinition_count_limits():
    with pytest.raises(ValidationError):
        EntityDefinition(count=0, fields={"id": FieldDefinition(type=FieldType.INTEGER)})


def test_blueprint_requires_entities():
    with pytest.raises(ValidationError, match="Blueprint должен содержать"):
        Blueprint(entities={})


def test_condition_and_action_roundtrip():
    cond = Condition(entity="orders", local_field="user_id", field="id", op="eq", value=5)
    act = Action(action="set", field="price", min=10, max=20)
    rule = Rule(if_=cond, then=act)

    entity = EntityDefinition(
        count=5,
        fields={"id": FieldDefinition(type=FieldType.INTEGER)},
        rules=[rule]
    )
    bp = Blueprint(entities={"orders": entity})
    req = GenerationRequest(blueprint=bp, seed=42)

    dumped = req.model_dump()
    assert dumped["blueprint"]["entities"]["orders"]["count"] == 5


def test_rule_field_alias_support():
    # Проверим, что "if" алиас работает
    rule_data = {
        "if": {
            "entity": "orders",
            "local_field": "user_id",
            "field": "id",
            "op": "eq",
            "value": 1
        },
        "then": {
            "action": "set",
            "field": "price",
            "min": 10,
            "max": 50
        }
    }
    rule = Rule.model_validate(rule_data)
    assert rule.if_.entity == "orders"
    assert rule.then.field == "price"
