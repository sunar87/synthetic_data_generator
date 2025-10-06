from typing import Any, Dict
from faker import Faker

from .registry import registry
from .models import FieldType
from .fields import FieldValueGenerator


@registry.register(FieldType.STRING)
class StringFieldGenerator(FieldValueGenerator):

    def __init__(self, faker: Faker, params: Dict[str, Any], field_name: str = None):
        super().__init__(faker, params)
        self.field_name = field_name

    def _generate_objects(self):
        if self.params.get('subtype') == 'name':
            return self.faker.name()
        if self.params.get('subtype') == 'first_name':
            return self.faker.first_name()
        if self.params.get('subtype') == 'last_name':
            return self.faker.last_name()
        if self.params.get('subtype') == 'email':
            return self.faker.email()
        if self.params.get('subtype') == 'address':
            return self.faker.address()
        if self.params.get('subtype') == 'job':
            return self.faker.job()

    def generate(self) -> str:
        special_subtype = self._generate_objects()
        if special_subtype:
            return special_subtype
        max_len = self.params.get("max_length", 20)
        return self.faker.text(max_nb_chars=max_len).strip()


@registry.register(FieldType.INTEGER)
class IntegerFieldGenerator(FieldValueGenerator):
    def generate(self) -> int:
        return self.faker.random_int(
            min=self.params.get("min", 0),
            max=self.params.get("max", 10000)
        )


@registry.register(FieldType.FLOAT)
class FloatFieldGenerator(FieldValueGenerator):
    def generate(self) -> float:
        return self.faker.pyfloat(
            min_value=self.params.get("min", 0.0),
            max_value=self.params.get("max", 1.0),
            right_digits=self.params.get("precision", 2)
        )


@registry.register(FieldType.BOOLEAN)
class BooleanFieldGenerator(FieldValueGenerator):
    def generate(self) -> bool:
        return self.faker.boolean()


@registry.register("reference")
class ReferenceFieldGenerator(FieldValueGenerator):
    """Генератор для ссылочных полей."""

    def __init__(self, faker: Faker, params: Dict[str, Any], context: Dict[str, Any]):
        super().__init__(faker, params)
        self.context = context

    def generate(self) -> Any:
        entity = self.params["entity"]
        field = self.params["field"]

        if entity not in self.context:
            raise ValueError(f"Сущность '{entity}' не найдена в контексте")
        if not self.context[entity]:
            raise ValueError(f"Нет доступных записей для сущности '{entity}'")

        ref_obj = self.faker.random_element(self.context[entity])
        return ref_obj[field]


@registry.register(FieldType.ONE_TO_MANY)
class OneToManyFieldGenerator(FieldValueGenerator):
    def generate(self):
        return []
