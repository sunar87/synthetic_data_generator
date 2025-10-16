import pytest
from core.models import Blueprint, EntityDefinition, FieldDefinition, FieldType, Rule, Condition, Action
from core.validators import validate_rules


def make_blueprint_with_ref(valid=True):
    user_fields = {
        "id": FieldDefinition(type=FieldType.INTEGER),
        "name": FieldDefinition(type=FieldType.STRING),
    }
    order_fields = {
        "id": FieldDefinition(type=FieldType.INTEGER),
        "user_id": FieldDefinition(type=FieldType.REFERENCE, params={"entity": "users", "field": "id"}),
        "price": FieldDefinition(type=FieldType.FLOAT),
    }

    users = EntityDefinition(count=5, fields=user_fields)
    orders = EntityDefinition(count=5, fields=order_fields)

    cond = Condition(entity="orders", local_field="user_id", field="id", op="eq", value=1)
    act = Action(action="set", field="price", min=100, max=500)
    rule = Rule(if_=cond, then=act)
    orders.rules = [rule]

    bp = Blueprint(entities={"users": users, "orders": orders})

    if not valid:
        del bp.entities["users"].fields["id"]

    return bp


def test_validate_rules_success():
    bp = make_blueprint_with_ref()
    validate_rules(bp)


def test_validate_rules_missing_field():
    bp = make_blueprint_with_ref(valid=False)
    with pytest.raises(ValueError, match="указывает на несуществующее поле"):
        validate_rules(bp)
