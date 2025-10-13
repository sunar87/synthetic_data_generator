import json
import pytest
from pydantic import ValidationError
from core.models import (
    FieldDefinition, FieldType,
    Condition, Action, Rule,
    EntityDefinition, Blueprint, GenerationRequest
)


def test_fielddefinition_roundtrip():
    fd = FieldDefinition(type=FieldType.STRING, params={"max_length": 20, "subtype": "name"})
    d = fd.to_dict()
    assert isinstance(d, dict)
    fd2 = FieldDefinition.from_dict(d)
    assert fd2.type == fd.type
    assert fd2.params == fd.params


def test_entity_and_rule_roundtrip():
    fd_int = FieldDefinition(type=FieldType.INTEGER, params={"min": 0, "max": 100})
    cond = Condition(entity="users", local_field="user_id", field="is_vip", op="eq", value=True)
    act = Action(action="set", field="price", min=1000, max=1200)
    rule = Rule(if_=cond, then=act)

    entity = EntityDefinition(count=2, fields={"id": fd_int, "price": fd_int}, rules=[rule])
    bp = Blueprint(entities={"orders": entity})

    bp_dict = bp.to_dict()
    # JSON-serializable
    s = json.dumps(bp_dict)
    assert '"orders"' in s

    bp2 = Blueprint.from_dict(bp_dict)
    assert "orders" in bp2.entities
    assert bp2.entities["orders"].count == 2
    # rule restored
    assert len(bp2.entities["orders"].rules) == 1
    restored_rule = bp2.entities["orders"].rules[0]
    assert restored_rule.if_.entity == "users"
    assert restored_rule.then.action == "set"


def test_generation_request_roundtrip_and_json_dump(tmp_path):
    fd = FieldDefinition(type=FieldType.UUID)
    ent = EntityDefinition(count=1, fields={"id": fd})
    bp = Blueprint(entities={"users": ent})
    req = GenerationRequest(blueprint=bp, seed=123)
    data = req.to_dict()

    # Записываем файл
    p = tmp_path / "req.json"
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # Загружаем обратно
    loaded = json.loads(p.read_text(encoding="utf-8"))
    req2 = GenerationRequest.from_dict(loaded)
    assert req2.seed == 123
    assert "users" in req2.blueprint.entities


def test_invalid_fieldparams_raises():
    with pytest.raises(ValidationError):
        # передаём недопустимый параметр для integer
        FieldDefinition(type=FieldType.INTEGER, params={"bogus": 1})
