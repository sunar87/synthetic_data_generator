from typing import Dict, List, Any
import random
from faker import Faker
from .models import Blueprint, FieldDefinition, FieldType
from .registry import registry


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
    if op == "in":
        return left in val
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


class DataGenerationEngine:
    """Движок генерации данных."""

    def __init__(self, seed: int = None):
        self.seed = seed
        self.faker = Faker()
        if seed is not None:
            random.seed(seed)
            self.faker.seed_instance(seed)

    def generate_entity(
        self,
        entity_name: str,
        definition: Dict[str, FieldDefinition],
        count: int,
        context: Dict[str, List[Dict[str, Any]]],
        rules: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:

        """Генерирует данные для одной сущности."""
        results = []

        for _ in range(count):
            generators = {
                fname: (
                    registry.create_instance(fdef.type.value, self.faker, fdef.params, context)
                    if fdef.type == FieldType.REFERENCE
                    else registry.create_instance(fdef.type.value, self.faker, fdef.params)
                )
                for fname, fdef in definition.items()
            }

            entity_data = {fname: gen.generate() for fname, gen in generators.items()}

            # Применяем правила
            if rules:
                for rule in rules:
                    if match_condition(entity_data, context, rule.if_):
                        apply_action(entity_data, self.faker, rule.then)

            results.append(entity_data)

        return results

    def execute(self, blueprint: Blueprint) -> Dict[str, List[Dict[str, Any]]]:
        results = {}
        context = {}

        for entity_name, entity_def in blueprint.entities.items():
            print(f"\n[DEBUG] Entity: {entity_name}")
            print(f"[DEBUG] Rules type: {type(entity_def.rules)}")
            print(f"[DEBUG] Rules content: {entity_def.rules}")
            generated = self.generate_entity(
                entity_name,
                entity_def.fields,
                entity_def.count,
                context,
                entity_def.rules
            )
            results[entity_name] = generated
            context[entity_name] = generated

        return results
