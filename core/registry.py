from typing import Dict, Type, Union, Any, Optional
from faker import Faker

from .fields import FieldValueGenerator
from .models import FieldType


class GeneratorRegistry:
    """Реестр генераторов (паттерн Registry), с поддержкой Enum FieldType."""

    def __init__(self):
        self._generators: Dict[FieldType, Type[FieldValueGenerator]] = {}

    def register(self, name: Union[str, FieldType]):
        """Декоратор для регистрации генератора."""
        def decorator(generator_cls: Type[FieldValueGenerator]):
            key = self._normalize_key(name)
            self._generators[key] = generator_cls
            return generator_cls
        return decorator

    def get_generator(self, name: Union[str, FieldType]) -> Type[FieldValueGenerator]:
        """Получить класс генератора по ключу (FieldType или строка)."""
        key = self._normalize_key(name)
        if key not in self._generators:
            raise ValueError(f"Generator '{name}' not registered")
        return self._generators[key]

    def create_instance(
        self,
        name: str,
        faker: Faker,
        params: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> FieldValueGenerator:
        generator_cls = self.get_generator(name)

        # Проверяем, принимает ли генератор context
        try:
            return generator_cls(faker, params, context)
        except TypeError:
            return generator_cls(faker, params)

    @staticmethod
    def _normalize_key(name: Union[str, FieldType]) -> FieldType:
        """Привести ключ к FieldType."""
        if isinstance(name, FieldType):
            return name
        return FieldType(name)


# Глобальный реестр
registry = GeneratorRegistry()
