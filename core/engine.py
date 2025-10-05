from typing import Dict, List, Any
import random
from faker import Faker

from .models import Blueprint, FieldDefinition, FieldType
from .registry import registry
from .validators import validate_rules
from .utils import match_condition, apply_action


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
        validate_rules(blueprint)
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
