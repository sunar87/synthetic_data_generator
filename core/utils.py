from faker import Faker


def match_condition(entity_data: dict, context: dict, cond: dict) -> bool:
    """
    Проверяет условие cond для текущей записи.
    cond: Condition (pydantic)
    """
    ent = cond.entity
    local_field = cond.local_field
    target_field = cond.field
    op = cond.op
    val = cond.value

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
        return left > val
    if op == "lt":
        return left < val
    return False


def apply_action(entity_data: dict, faker: Faker, action: dict):
    """
    Применяет действие action к entity_data.
    """
    field_name = action.field
    act = action.action

    if act == "set":
        entity_data[field_name] = faker.random_int(
            min=action.min or 0,
            max=action.max or 10000
        )
    elif act == "adjust":
        cur = entity_data.get(field_name, 0)
        min_v = action.min
        if min_v is not None and cur < min_v:
            entity_data[field_name] = faker.random_int(
                min=min_v,
                max=action.max or (min_v * 2)
            )
