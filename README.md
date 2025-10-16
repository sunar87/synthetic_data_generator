# Synthetic Data Generator

# 🧬 Synthetic Data Generator

**Synthetic Data Generator** — это мощный и гибкий инструмент для декларативного описания и генерации связанных структур данных.  
Проект создан для разработчиков, аналитиков и ML-инженеров, которым нужно **реалистично выглядящее тестовое или обучающее окружение** без необходимости ручного ввода данных.

---
## 📖 Оглавление
1. [Возможности](#-возможности)
2. [Требования и установка](#-требования-и-установка)
3. [Quickstart](#-quickstart)
4. [Архитектура](#-архитектура)
5. [Примеры запросов](#-пример-запроса)
6. [Основные сущности](#-основные-сущности)
7. [Поддерживаемые типы полей](#-поддерживаемые-типы-полей-fieldtype)
8. [Rules (Правила)](#-rules-правила)
9. [Пример результата](#-пример-результата)
10. [Расширение функционала](#-расширение-функционала)
11. [Применение](#-применение)
12. [Связь с разработчиком](#-связь-с-разработчиком)
13. [Лицензия](#-лицензия)
---

## 🚀 Возможности

- 🔗 **Поддержка связей между сущностями** (`reference`, `one_to_many`).
- 🧩 **Гибкая декларация сущностей** в формате JSON через поле `blueprint`.
- 🧠 **Правила (`rules`)** для условной генерации и модификации данных.
- 🧍‍♂️ **Автоматическое построение зависимостей** (topological sort) для правильного порядка генерации.
- 🎲 **Детерминированность по seed** — одинаковый seed = одинаковые данные.
- 🧰 **Расширяемая система типов полей** через реестр (`registry`).
- 🪄 **Автоматическая подстановка связей** (embed или ID) в зависимости от настроек.
- 🧱 **Поддержка вложенных структур** (встраивание дочерних сущностей в родительские).

---

## 💻 Требования и установка

Для запуска проекта необходимо поднять Docker контейнер:

```bash
docker compose up -d --build
```
---


## 🔌 Quickstart

Простейший пример генерации 3 пользователей:

```bash
from core.models import GenerationRequest, Blueprint
from core.engine import DataGenerationEngine

blueprint = Blueprint(
    entities={
        "users": {
            "count": 3,
            "fields": {
                "id": { "type": "integer" },
                "name": { "type": "string", "params": { "subtype": "name" } },
                "is_vip": { "type": "boolean" }
            }
        }
    }
)

request = GenerationRequest(blueprint=blueprint, seed=42)
engine = DataGenerationEngine(seed=request.seed)
result = engine.execute(request.blueprint)

print(result)
```
---

## 🧠 Архитектура

Генератор построен на трёх ключевых компонентах:

1. **Blueprint** — декларативное описание схемы данных.  
   Содержит все сущности, поля, связи и правила.
2. **DataGenerationEngine** — ядро генерации.  
   Отвечает за порядок, зависимости, генерацию и применение правил.
3. **Registry** — фабрика типов полей.  
   Позволяет легко добавлять новые генераторы (например, `uuid`, `email`, `address`).

   **Ниже представлена наглядная схема генерации данных**

```
 +---------------------+
|     JSON Blueprint  |
|  (entities + rules) |
+----------+----------+
           |
           v
+---------------------+
| DataGenerationEngine|
|  - Topological sort |
|  - Field generators |
|  - Apply rules      |
|  - Resolve relations|
+----------+----------+
           |
           v
+---------------------+
|      Output JSON    |
|  - Linked entities  |
|  - Rules applied    |
+----------+----------+
           |
   +-------+--------+
   |                |
   v                v
API Response      Database
(/api/download/...)  (*in development. will be soon*)
```

---

## 📜 Пример запроса

### 1. Простые поля (STRING, INTEGER, BOOLEAN)

```json
{
  "seed": 42,
  "blueprint": {
    "entities": {
      "users": {
        "count": 3,
        "fields": {
          "id": { "type": "integer" },
          "name": { "type": "string", "params": { "subtype": "name" } },
          "is_vip": { "type": "boolean" }
        }
      }
    }
  }
}
```

---

### 2. Reference (один к одному/foreign key)

```json
{
  "seed": 101,
  "blueprint": {
    "entities": {
      "users": {
        "count": 2,
        "fields": {
          "id": { "type": "integer" },
          "name": { "type": "string" }
        }
      },
      "orders": {
        "count": 5,
        "fields": {
          "id": { "type": "integer" },
          "product": { "type": "string" },
          "user_id": { "type": "reference", "params": { "entity": "users", "field": "id" } }
        }
      }
    }
  }
}
```

---

### 3. One-to-Many (встраивание зависимых сущностей)

```json
{
  "seed": 202,
  "blueprint": {
    "entities": {
      "users": {
        "count": 3,
        "fields": {
          "id": { "type": "integer" },
          "name": { "type": "string" },
          "orders": {
            "type": "one_to_many",
            "params": {
              "entity": "orders",
              "foreign_field": "user_id",
              "embed": true
            }
          }
        }
      },
      "orders": {
        "count": 6,
        "fields": {
          "id": { "type": "integer" },
          "product": { "type": "string" },
          "user_id": { "type": "reference", "params": { "entity": "users", "field": "id" } }
        }
      }
    }
  }
}
```

---

### 4. Reference + One-to-Many (условия + вложенные связи)

```json
{
  "seed": 303,
  "blueprint": {
    "entities": {
      "users": {
        "count": 3,
        "fields": {
          "id": { "type": "integer" },
          "name": { "type": "string", "params": { "subtype": "name" } },
          "is_vip": { "type": "boolean" },
          "orders": {
            "type": "one_to_many",
            "params": {
              "entity": "orders",
              "foreign_field": "user_id",
              "embed": true
            }
          }
        }
      },
      "orders": {
        "count": 6,
        "fields": {
          "id": { "type": "integer" },
          "product": { "type": "string" },
          "price": { "type": "integer", "params": { "min": 10, "max": 500 } },
          "user_id": { "type": "reference", "params": { "entity": "users", "field": "id" } }
        },
        "rules": [
          {
            "if": {
              "entity": "users",
              "local_field": "user_id",
              "field": "is_vip",
              "op": "eq",
              "value": true
            },
            "then": {
              "action": "set",
              "field": "price",
              "min": 1000,
              "max": 1200
            }
          }
        ]
      }
    }
  }
}
```
---

## 🧩 Основные сущности

### 🧱 Blueprint

Главный объект, описывающий всё, что нужно сгенерировать.

| Поле | Тип | Описание |
|------|------|-----------|
| `entities` | `dict` | Словарь с описанием всех сущностей. |
| `seed` | `int` *(опционально)* | Фиксирует генератор случайных чисел для повторяемости результатов. |

---

### 🧍‍♂️ Entity (Сущность)

Определяет структуру данных одной таблицы или набора записей.

| Поле | Тип | Описание |
|------|------|-----------|
| `count` | `int` | Количество записей для генерации. |
| `fields` | `dict` | Описание каждого поля в записи. |
| `rules` | `list` *(опционально)* | Набор условий для изменения сгенерированных данных. |

---

## 🔢 Поддерживаемые типы полей (`FieldType`)

| Тип | Описание | Пример значения |
|------|-----------|----------------|
| `string` | Текстовые данные, случайные строки или имена | `"John Doe"` |
| `integer` | Целые числа в заданном диапазоне | `42` |
| `float` | Вещественные числа (с плавающей точкой) | `3.14` |
| `boolean` | Логическое значение | `true` / `false` |
| `uuid` | uuid v4 | `fe342a0c-c2ae-4f65-bfd8-19c030033c09` |
| `email` | Email поле | `test@gmail.com` |
| `reference` | Ссылка на другую сущность (Foreign Key) | `user_id = users.id` |
| `one_to_many` | Вложенные данные (список связанных элементов) | `orders: [ {id: 1, ...} ]` |

---

## ⚙️ Параметры params для каждого типа поля

| Тип поля | Допустимые параметры (`params`) | Пример |
|-----------|----------------------------------|--------|
| **string** | `min_length`, `max_length`, `subtype` (например, `"name"`, `"email"`, `"address"`) | `"params": {"max_length": 10, "subtype": "name"}` |
| **integer** | `min`, `max` | `"params": {"min": 10, "max": 500}` |
| **float** | `min`, `max`, `precision` (число знаков после запятой) | `"params": {"min": 0.0, "max": 1.0, "precision": 2}` |
| **boolean** | — | `{ "type": "boolean" }` |
| **reference (foreign key)** | `entity` (на какую сущность ссылается), `field` (какое поле используется) | `"params": {"entity": "users", "field": "id"}` |
| **one_to_many** | `entity` (дочерняя сущность), `foreign_field`, `parent_field` (по умолчанию `id`), `embed` (встраивать ли объекты внутрь) | `"params": {"entity": "orders", "foreign_field": "user_id", "embed": true}` |

---

### 🧠 Rules (Правила)

Механизм условных действий над данными.

**Структура:**

```json
{
  "if": {
    "entity": "users",
    "local_field": "user_id",
    "field": "is_vip",
    "op": "eq",
    "value": true
  },
  "then": {
    "action": "set",
    "field": "price",
    "min": 1000,
    "max": 1200
  }
}
```

**Поддерживаемые операторы:**
- `eq` — равно
- `neq` — не равно
- `gt` — больше
- `lt` — меньше


**Поддерживаемые действия:**
- `set` — установить новое значение в заданном диапазоне
- `adjust` — корректирует текущее значение, если оно не попадает в границы min

---

## ⚙️ Логика генерации

1. 🔍 **Topological sort**  
   Определяет порядок генерации сущностей (например, `users` → `orders`), чтобы ссылки `reference` корректно разрешались.

2. 🏗 **Генерация полей**  
   Каждый тип поля создаётся через `registry`, который использует `Faker` и параметры поля.

3. 🧠 **Применение правил (`rules`)**  
   После генерации сущности выполняются условия и действия, модифицирующие данные.

4. 🔁 **Решение связей (`one_to_many`)**  
   После генерации всех сущностей родитель получает список связанных дочерних записей (либо их ID).

---

## 🧰 Пример результата

```json
{
  "status": "success",
  "data": {
    "users": [
      {
        "id": 1824,
        "name": "Ago site face.",
        "is_vip": true,
        "orders": [
          {
            "id": 6873,
            "product": "Discussion list.",
            "price": 1187,
            "user_id": 1824
          }
        ]
      }
    ]
  }
}
```

---

## 🧩 Расширение функционала

Добавить новый тип поля просто:
1. Зарегистрируй класс в `registry.py`.
2. Определи метод `.generate()`.
3. Используй его в `blueprint`.

---

## 💡 Применение

- Тестирование REST API
- Обогащение демо-данных
- Генерация синтетических наборов для ML
- Создание mock-сервисов и sandbox-окружений

---


## 📞 Связь в разработчиком

- https://Github.com/sunar87 - github
- @sunar877 - Telegram
- sunar877@yandex.ru - email

## 🧾 Лицензия

MIT © 2025 — Разработано с ❤️ специально для гибкой генерации данных.
