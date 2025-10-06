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
        context: Optional[Dict[str, Any]] = None,
        field_name: Optional[str] = None
    ) -> FieldValueGenerator:
        generator_cls = self.get_generator(name)

        try:
            return generator_cls(faker, params, context)
        except TypeError:
            pass

        try:
            return generator_cls(faker, params, field_name)
        except TypeError:
            pass

        try:
            return generator_cls(faker, params)
        except TypeError as e:
            raise TypeError(f"Cannot instantiate generator {generator_cls}: {e}")

    @staticmethod
    def _normalize_key(name: Union[str, FieldType]) -> FieldType:
        """Привести ключ к FieldType."""
        if isinstance(name, FieldType):
            return name
        return FieldType(name)


# Глобальный реестр
registry = GeneratorRegistry()
