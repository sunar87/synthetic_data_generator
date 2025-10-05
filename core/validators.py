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
            if target_fdef.type == FieldType.STRING:
                raise ValueError(
                    f"[Ошибка] Для STRING поля '{cond_field}' "
                    f"нет допустимых операторов"
                )
