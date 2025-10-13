from .models import Blueprint, FieldType


def validate_rules(blueprint: Blueprint):
    """
    Проверяет корректность правил (rules) в blueprint.
    """
    for entity_name, entity_def in blueprint.entities.items():
        rules = getattr(entity_def, "rules", []) or []

        for idx, rule in enumerate(rules):
            cond = rule.if_
            lf = cond.local_field
            fdef = entity_def.fields.get(lf)
            then_field = rule.then.field
            if not fdef:
                raise ValueError(
                    f"[Ошибка] В rules[{idx}] сущности '{entity_name}' указано "
                    f"несуществующее local_field '{lf}'"
                )

            if fdef.type != FieldType.REFERENCE:
                raise ValueError(
                    f"[Ошибка] local_field '{lf}' в rules[{idx}] сущности '{entity_name}' "
                    f"должен быть типа REFERENCE"
                )

            if then_field not in entity_def.fields:
                raise ValueError(
                    f"[Ошибка] В rules[{idx}] сущности '{entity_name}' указано действие "
                    f"для несуществующего поля '{then_field}'"
                )

            if rule.then.action not in {"set", "adjust"}:
                raise ValueError(
                    f"[Ошибка] В rules[{idx}] сущности '{entity_name}' указано "
                    f"недопустимое действие '{rule.then.action}'"
                )

            if rule.then.action == "set":
                min_val, max_val = rule.then.min, rule.then.max
                if min_val is not None and max_val is not None and min_val > max_val:
                    raise ValueError(
                        f"[Ошибка] В rules[{idx}] min ({min_val}) не может быть больше max ({max_val})"
                    )

            ref_entity = fdef.params.get("entity")
            ref_field = fdef.params.get("field")

            if ref_entity not in blueprint.entities:
                raise ValueError(
                    f"[Ошибка] Reference в поле '{lf}' rules[{idx}] "
                    f"указывает на несуществующую сущность '{ref_entity}'"
                )
            if ref_field not in blueprint.entities[ref_entity].fields:
                raise ValueError(
                    f"[Ошибка] Reference в поле '{lf}' rules[{idx}] "
                    f"указывает на несуществующее поле '{ref_field}' в сущности '{ref_entity}'"
                )

            cond_field = cond.field
            if cond_field not in blueprint.entities[ref_entity].fields:
                raise ValueError(
                    f"[Ошибка] В rules[{idx}] сущности '{entity_name}' "
                    f"if.field '{cond_field}' не существует в сущности '{ref_entity}'"
                )

            target_fdef = blueprint.entities[ref_entity].fields[cond_field]

            if target_fdef.type == FieldType.BOOLEAN and cond.op not in {"eq", "neq"}:
                raise ValueError(
                    f"[Ошибка] Для BOOLEAN поля '{cond_field}' "
                    f"разрешены только операторы eq/neq, но указан '{cond.op}'"
                )
            if target_fdef.type in {FieldType.INTEGER, FieldType.FLOAT} and cond.op not in {"eq", "neq", "gt", "lt"}:
                raise ValueError(
                    f"[Ошибка] Для числового поля '{cond_field}' "
                    f"недопустимый оператор '{cond.op}'"
                )
            if target_fdef.type == FieldType.STRING and cond.op not in {"eq", "neq"}:
                raise ValueError(
                    f"[Ошибка] Для STRING поля '{cond_field}' "
                    f"нет допустимых операторов"
                )


def validate_one_to_many(blueprint: Blueprint) -> bool:
    """
    Проверяет корректность one-to-many связей в blueprint.
    Если таких связей нет — просто возвращает True.
    """

    for entity_name, entity_def in blueprint.entities.items():
        for field_name, field_def in entity_def.fields.items():
            if field_def.type == FieldType.REFERENCE:
                ref_entity = field_def.params.get("entity")
                ref_field = field_def.params.get("field")

                if not ref_entity or not ref_field:
                    raise ValueError(
                        f"[Ошибка] Поле '{field_name}' в сущности '{entity_name}' "
                        f"имеет некорректную reference-ссылку."
                    )
                if ref_entity not in blueprint.entities:
                    raise ValueError(
                        f"[Ошибка] Reference в '{entity_name}.{field_name}' "
                        f"указывает на несуществующую сущность '{ref_entity}'."
                    )
                if ref_field not in blueprint.entities[ref_entity].fields:
                    raise ValueError(
                        f"[Ошибка] Reference в '{entity_name}.{field_name}' "
                        f"указывает на несуществующее поле '{ref_field}'."
                    )
            elif field_def.type == FieldType.ONE_TO_MANY:
                params = field_def.params or {}
                child_entity = params.get("entity")
                foreign_field = params.get("foreign_field")

                if not child_entity or not foreign_field:
                    raise ValueError(
                        f"[Ошибка] Поле '{field_name}' в сущности '{entity_name}' "
                        f"должно содержать параметры 'entity' и 'foreign_field'."
                    )

                # Проверяем, что дочерняя сущность существует
                if child_entity not in blueprint.entities:
                    raise ValueError(
                        f"[Ошибка] ONE_TO_MANY '{entity_name}.{field_name}' "
                        f"указывает на несуществующую сущность '{child_entity}'."
                    )

                # Проверяем, что foreign_field существует
                child_fields = blueprint.entities[child_entity].fields
                if foreign_field not in child_fields:
                    raise ValueError(
                        f"[Ошибка] ONE_TO_MANY '{entity_name}.{field_name}' "
                        f"указывает на несуществующее поле '{foreign_field}' "
                        f"в сущности '{child_entity}'."
                    )

                # Проверяем, что foreign_field — типа REFERENCE
                if child_fields[foreign_field].type != FieldType.REFERENCE:
                    raise ValueError(
                        f"[Ошибка] Поле '{foreign_field}' в дочерней сущности '{child_entity}' "
                        f"должно быть типа REFERENCE для связи '{entity_name}.{field_name}'."
                    )
    return True
