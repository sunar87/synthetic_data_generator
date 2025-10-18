# 🧾 Changelog

## [1.0.0] - 2025-10-18
### 🚀 Added
- Первая стабильная версия Synthetic Data Generator.
- Поддержка всех типов полей: `string`, `integer`, `float`, `boolean`, `uuid`, `email`, `reference`, `one_to_many`.
- Механизм правил (`rules`) с действиями `set` и `adjust`.
- Валидация схемы `blueprint` на уровне Pydantic-моделей.
- API маршруты:
  - `POST /api/generate` — генерация данных
  - `GET /api/download/{filename}` — скачивание результата
  - `GET /api/health` — проверка состояния сервера
- Поддержка детерминированных результатов по `seed`.
- Сборка проекта через Docker и Docker Compose.
- README и документация с примерами использования.

### 🧩 Improved
- Упрощена структура `core/engine.py` и `core/validators.py`.
- Улучшена читаемость логов через централизованный логгер.
- Добавлены тесты для всех основных модулей (coverage ≈ 100%).

### 🐞 Fixed
- Исправлены ошибки при обработке `rules`, `reference` и `one_to_many`.
- Устранены проблемы с зависимостями между сущностями (topo sort).
- Исправлен баг с `download_url` в JSON-ответах.

---
