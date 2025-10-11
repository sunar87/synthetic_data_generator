from typing import Dict, List, Any
from collections import defaultdict, deque
from faker import Faker

from .models import Blueprint, FieldDefinition, FieldType
from .registry import registry
from .utils import match_condition, apply_action


def topo_sort(blueprint):
    """
    Выполняет топологическую сортировку сущностей по зависимостям reference-полей.
    Нужно, чтобы сначала генерировать независимые сущности (users), а потом зависимые (orders).
    """
    graph = defaultdict(list)
    indegree = defaultdict(int)

    for entity_name, entity_def in blueprint.entities.items():
        indegree.setdefault(entity_name, 0)
        for field_def in entity_def.fields.values():
            if field_def.type.name == "REFERENCE":
                ref_entity = field_def.params.get("entity")
                if ref_entity:
                    graph[ref_entity].append(entity_name)
                    indegree[entity_name] += 1

    # Топологическая сортировка (Kahn’s algorithm)
    queue = deque([name for name, deg in indegree.items() if deg == 0])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for dependent in graph[node]:
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                queue.append(dependent)

    if len(order) != len(indegree):
        raise ValueError("Обнаружена циклическая зависимость между сущностями")

    return order


class DataGenerationEngine:
    def __init__(self, seed: int = None):
        self.seed = seed
        self.faker = Faker()
        if seed is not None:
            import random
            random.seed(seed)
            self.faker.seed_instance(seed)

    def _apply_rules(
        self,
        entity_name: str,
        entity_data_list: List[Dict[str, Any]],
        blueprint: Blueprint,
        context: Dict[str, List[Dict[str, Any]]]
    ):
        """Применяет правила rules для каждой записи сущности, используя match_condition и apply_action."""
        entity_def = blueprint.entities[entity_name]
        for entity_data in entity_data_list:
            for rule in getattr(entity_def, "rules", []):
                cond = rule.if_
                action = rule.then

                if match_condition(entity_data, context, cond):
                    apply_action(entity_data, self.faker, action)

    def generate_entity(
            self,
            entity_name: str,
            definition: Dict[str, FieldDefinition],
            count: int,
            context: Dict[str, List[Dict[str, Any]]]
            ) -> List[Dict[str, Any]]:
        results = []
        generators = {
            fname: registry.create_instance(
                fdef.type.value,
                self.faker,
                fdef.params,
                context=context if fdef.type == FieldType.REFERENCE else None,
                field_name=fname
            )
            for fname, fdef in definition.items()
        }

        for _ in range(count):
            entity_data = {fname: gen.generate() for fname, gen in generators.items()}
            results.append(entity_data)

        return results

    def _resolve_one_to_many(
            self,
            context: Dict[str, List[Dict[str, Any]]],
            parent_entity: str, field_name: str, fdef: FieldDefinition,
            blueprint: Blueprint
            ):
        child_entity = fdef.params["entity"]
        foreign_field = fdef.params["foreign_field"]
        parent_field = fdef.params.get("parent_field", "id")
        embed = bool(fdef.params.get("embed", False))
        child_def = blueprint.entities[child_entity]

        if foreign_field not in child_def.fields:
            raise ValueError(
                f"Поле '{foreign_field}' отсутствует в сущности '{child_entity}'"
            )

        foreign_field_def = child_def.fields[foreign_field]
        if foreign_field_def.type.name != "REFERENCE":
            raise ValueError(
                f"Поле '{foreign_field}' в '{child_entity}' должно быть типа REFERENCE, "
                f"а не {foreign_field_def.type.name}"
            )
        index = {}
        for child in context.get(child_entity, []):
            key = child.get(foreign_field)
            if key is None:
                continue
            index.setdefault(key, []).append(child)

        for parent in context.get(parent_entity, []):
            children = index.get(parent.get(parent_field), [])
            if embed:
                parent[field_name] = [child.copy() for child in children]
            else:
                parent[field_name] = [child.get("id") for child in children]

    def execute(self, blueprint: Blueprint) -> Dict[str, List[Dict[str, Any]]]:
        results: Dict[str, List[Dict[str, Any]]] = {}
        context: Dict[str, List[Dict[str, Any]]] = {}

        order = topo_sort(blueprint)

        for entity_name in order:
            entity_def = blueprint.entities[entity_name]
            generated = self.generate_entity(
                entity_name,
                entity_def.fields,
                entity_def.count,
                context
            )
            results[entity_name] = generated
            context[entity_name] = generated

        self._apply_rules(entity_name, generated, blueprint, context)

        for parent_entity, parent_def in blueprint.entities.items():
            for fname, fdef in parent_def.fields.items():
                if fdef.type == FieldType.ONE_TO_MANY:
                    self._resolve_one_to_many(
                        context,
                        parent_entity,
                        fname,
                        fdef,
                        blueprint
                    )

        return results
