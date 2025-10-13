from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


class FieldType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    UUID = "uuid"
    FLOAT = "float"
    EMAIL = "email"
    BOOLEAN = "boolean"
    REFERENCE = "reference"
    ONE_TO_MANY = "one_to_many"


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
            allowed = {"min_length", "max_length", "subtype"}
        elif field_type == FieldType.INTEGER:
            allowed = {"min", "max"}
        elif field_type == FieldType.FLOAT:
            allowed = {"min", "max", "precision"}
        elif field_type == FieldType.BOOLEAN:
            allowed = set()
        elif field_type == FieldType.REFERENCE:
            allowed = {"entity", "field"}
        elif field_type == FieldType.ONE_TO_MANY:
            allowed = {"entity", "foreign_field", "embed", "parent_field"}
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

    def to_dict(self):
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


class Condition(BaseModel):
    entity: str
    local_field: str
    field: str
    op: str = "eq"
    value: Any

    def to_dict(self):
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


class Action(BaseModel):
    action: str
    field: str
    min: Optional[int] = None
    max: Optional[int] = None

    def to_dict(self):
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


class Rule(BaseModel):
    if_: Condition = Field(alias="if")
    then: Action

    model_config = ConfigDict(populate_by_name=True)

    def to_dict(self):
        return {
            "if": self.if_.to_dict(),
            "then": self.then.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            if_=Condition.from_dict(data["if"]),
            then=Action.from_dict(data["then"]),
        )


class EntityDefinition(BaseModel):
    """Описание одной сущности"""
    count: int = Field(gt=0, le=5000, description="Количество записей")
    fields: Dict[str, FieldDefinition]
    rules: List[Rule] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")

    @field_validator("fields")
    def validate_fields_not_empty(cls, v):
        if not v:
            raise ValueError("У сущности должно быть хотя бы одно поле")
        return v

    def to_dict(self):
        return {
            "count": self.count,
            "fields": {k: v.to_dict() for k, v in self.fields.items()},
            "rules": [r.to_dict() for r in self.rules],
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            count=data["count"],
            fields={k: FieldDefinition.from_dict(v) for k, v in data.get("fields", {}).items()},
            rules=[Rule.from_dict(r) for r in data.get("rules", [])],
        )


class Blueprint(BaseModel):
    """Чертёж, описывающий набор сущностей"""
    entities: Dict[str, EntityDefinition]

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_entities(self):
        if not self.entities:
            raise ValueError("Blueprint должен содержать хотя бы одну сущность")
        return self

    def to_dict(self):
        return {"entities": {k: v.to_dict() for k, v in self.entities.items()}}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            entities={k: EntityDefinition.from_dict(v) for k, v in data.get("entities", {}).items()}
        )


class GenerationRequest(BaseModel):
    """Запрос на генерацию данных по чертежу"""
    blueprint: Blueprint
    seed: Optional[int] = None

    model_config = ConfigDict(extra="forbid")

    def to_dict(self):
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
