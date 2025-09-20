from core import DataGenerationEngine, registry, Blueprint, GenerationRequest
import json


def main():
    blueprint_config = {
        "entities": {
            "users": {
                "count": 3,
                "fields": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"}
                }
            },
            "orders": {
                "count": 5,
                "fields": {
                    "id": {"type": "integer"},
                    "product": {"type": "string"},
                    "user_id": {
                        "type": "reference",
                        "params": {"entity": "users", "field": "id"}
                    }
                }
            }
        }
    }

    request = GenerationRequest(
        blueprint=Blueprint(**blueprint_config),
        seed=425
    )

    engine = DataGenerationEngine(seed=request.seed)
    result = engine.execute(request.blueprint)

    print(json.dumps(result, indent=2, ensure_ascii=False))

    with open("generated.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
