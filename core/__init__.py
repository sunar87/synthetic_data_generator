# core/__init__.py
# Здесь мы делаем пакет удобным для импорта

# Импортируем реестр
from .registry import registry

# Импортируем движок
from .engine import DataGenerationEngine

# Импортируем модели
from .models import FieldType, FieldDefinition, EntityDefinition, Blueprint, GenerationRequest

# Импортируем генераторы, чтобы они автоматически зарегистрировались
from . import generators

__all__ = [
    "registry",
    "DataGenerationEngine",
    "FieldType",
    "FieldDefinition",
    "EntityDefinition",
    "Blueprint",
    "GenerationRequest",
]
