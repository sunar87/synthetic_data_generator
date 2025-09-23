from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


class FieldType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    REFERENCE = "reference"


class FieldDefinition(BaseModel):
    """Описание одного поля сущности"""
    type: FieldType
    params: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid")

    @field_validator("params")
    def validate_params(cls, v, info):
        """Пример проверки параметров в зависимости от типа"""
        field_type = info.data.get("type")
        if field_type == FieldType.STRING:
            allowed = {"min_length", "max_length"}
        elif field_type == FieldType.INTEGER:
            allowed = {"min", "max"}
        elif field_type == FieldType.FLOAT:
            allowed = {"min", "max", "precision"}
        elif field_type == FieldType.BOOLEAN:
            allowed = set()
        elif field_type == FieldType.REFERENCE:
            allowed = {"entity", "field"}
        else:
            allowed = set()

        extra = set(v.keys()) - allowed
        if extra:
            raise ValueError(f"Недопустимые параметры для {field_type}: {extra}")
        return v

    @model_validator(mode="after")
    def check_reference_params(self):
        """Дополнительная проверка для reference"""
        if self.type == FieldType.REFERENCE:
            if "entity" not in self.params or "field" not in self.params:
                raise ValueError(
                    "Для FieldType.REFERENCE обязательны параметры: 'entity' и 'field'"
                )
        return self


class Condition(BaseModel):
    entity: str
    local_field: str
    field: str
    op: str = "eq"        # eq, neq, gt, lt, in
    value: Any


class Action(BaseModel):
    action: str
    field: str
    min: Optional[int] = None
    max: Optional[int] = None


class Rule(BaseModel):
    if_: Condition = Field(alias="if")
    then: Action


class EntityDefinition(BaseModel):
    """Описание одной сущности"""
    count: int = Field(gt=0, le=100_000, description="Количество записей")
    fields: Dict[str, FieldDefinition]
    rules: List[Rule] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")

    @field_validator("fields")
    def validate_fields_not_empty(cls, v):
        if not v:
            raise ValueError("У сущности должно быть хотя бы одно поле")
        return v


class Blueprint(BaseModel):
    """Чертёж, описывающий набор сущностей"""
    entities: Dict[str, EntityDefinition]

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_entities(self):
        if not self.entities:
            raise ValueError("Blueprint должен содержать хотя бы одну сущность")
        return self


class GenerationRequest(BaseModel):
    """Запрос на генерацию данных по чертежу"""
    blueprint: Blueprint
    seed: Optional[int] = None

    model_config = ConfigDict(extra="forbid")
