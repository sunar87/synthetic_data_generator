from faker import Faker


def match_condition(entity_data: dict, context: dict, cond: dict) -> bool:
    """
    Проверяет условие cond для текущей записи.
    cond: Condition (pydantic)
    """
    ent = getattr(cond, "entity", None) or cond.get("entity")
    local_field = getattr(cond, "local_field", None) or cond.get("local_field")
    target_field = getattr(cond, "field", None) or cond.get("field")
    op = getattr(cond, "op", None) or cond.get("op")
    val = getattr(cond, "value", None) or cond.get("value")

    if ent not in context:
        return False

    fk = entity_data.get(local_field)
    if fk is None:
        return False

    ref_obj = next((o for o in context[ent] if o.get("id") == fk), None)
    if not ref_obj:
        return False

    left = ref_obj.get(target_field)

    if op == "eq":
        return left == val
    if op == "neq":
        return left != val
    if op == "gt":
        try:
            return left > val
        except TypeError:
            return False
    if op == "lt":
        try:
            return left < val
        except TypeError:
            return False
    if op == "in":
        try:
            return left in val
        except Exception:
            return False
    return False


def apply_action(entity_data: dict, faker: Faker, action: dict):
    """
    Применяет действие action к entity_data.
    """
    field_name = getattr(action, "field", None) or action.get("field")
    act = getattr(action, "action", None) or action.get("action")

    if act == "set":
        entity_data[field_name] = faker.random_int(
            min=getattr(action, "min", None) or action.get("min", 0),
            max=getattr(action, "max", None) or action.get("max", 10000)
        )
    elif act == "adjust":
        cur = entity_data.get(field_name, 0)
        min_v = getattr(action, "min", None) or action.get("min")
        max_v = getattr(action, "max", None) or action.get("max")
        if min_v is not None and cur < min_v:
            entity_data[field_name] = faker.random_int(
                min=min_v,
                max=max_v or (min_v * 2)
            )
