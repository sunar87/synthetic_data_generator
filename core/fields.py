from abc import ABC, abstractmethod
from typing import Any, Dict
from faker import Faker


class FieldValueGenerator(ABC):
    """Абстрактный базовый класс для всех генераторов полей."""

    def __init__(self, faker: Faker, params: Dict[str, Any]):
        self.faker = faker
        self.params = params

    @abstractmethod
    def generate(self) -> Any:
        """Сгенерировать значение."""
        ...
