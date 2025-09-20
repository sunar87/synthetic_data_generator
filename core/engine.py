from typing import Dict, List, Any
import random
from faker import Faker
from .models import Blueprint, FieldDefinition, FieldType
from .registry import registry


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
        context: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Генерирует данные для одной сущности."""
        results = []

        # создаём генераторы для всех полей
        generators = {
            fname: (
                registry.create_instance(fdef.type.value, self.faker, fdef.params, context)
                if fdef.type == FieldType.REFERENCE
                else registry.create_instance(fdef.type.value, self.faker, fdef.params)
            )
            for fname, fdef in definition.items()
        }

        # генерируем записи
        for _ in range(count):
            entity_data = {fname: gen.generate() for fname, gen in generators.items()}
            results.append(entity_data)

        return results

    def execute(self, blueprint: Blueprint) -> Dict[str, List[Dict[str, Any]]]:
        """Выполняет генерацию данных по blueprint."""
        results: Dict[str, List[Dict[str, Any]]] = {}

        for entity_name, entity_def in blueprint.entities.items():
            results[entity_name] = self.generate_entity(
                entity_name,
                entity_def.fields,
                entity_def.count,
                context=results  # передаём уже сгенерированные данные
            )

        return results
