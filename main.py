from core import DataGenerationEngine, registry, Blueprint, GenerationRequest
import json


def main():
    blueprint_config = {
     "entities": {
        "users": {
            "count": 3,
            "fields": {
                "id": {"type": "integer"},
                "name": {"type": "string", "params": {"max_length": 10}},
                "is_vip": {"type": "boolean"}
            }
            },
        "orders": {
            "count": 5,
            "fields": {
                "id": {"type": "integer"},
                "product": {"type": "string", "params": {"max_length": 15}},
                "price": {"type": "integer", "params": {"min": 10, "max": 500}},
                "user_id": {"type": "reference", "params": {"entity": "users", "field": "id"}}
            },
            "rules": [
                {
                    "if": {"entity": "users", "local_field": "user_id", "field": "is_vip", "op": "eq", "value": True},
                    "then": {"action": "set", "field": "price", "min": 1000, "max": 1001}
                }
            ]
            }
        }
    }

    request = GenerationRequest(
        blueprint=Blueprint(**blueprint_config),
        seed=415
    )

    engine = DataGenerationEngine(seed=request.seed)
    result = engine.execute(request.blueprint)

    print(json.dumps(result, indent=2, ensure_ascii=False))

    with open("generated.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
