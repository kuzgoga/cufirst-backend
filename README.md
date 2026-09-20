# CU:Hack

## Getting started
0. uv можно скачать [тут](https://docs.astral.sh/uv/)

Установка зависимостей:
```bash
uv sync
```

Запуск:
```bash
uv run dev
```

Форматирование:
```bash
uv format
```

Линтинг
```bash
uv run ruff check .
```

Если вы тоже не любите видеть `__pychache__`:
```python
PYTHONDONTWRITEBYTECODE=1 uv run dev
```

## Свагер
http://localhost:8000/schema/scalar#GET/me

## Миграции
Создание миграции:
```bash
uv run alembic revision --autogenerate -m "describe_change"
```

Применение миграции:
```bash
uv run alembic upgrade head
```

!!!
Миграции запускются и сиды данных при старте, будь осторожен.

## Кодекс чести
1. Unified Response. ВСЕ ответы должны иметь единый тип:
Успешный ответ:  
```json
{
    "status": "success",
    "data": {...},
}
```
Неудачный ответ:  
```json
{
  "status":"error",
  "code":"UNKNOWN_ERROR",
  "message":"Неизвестная ошибка"
}
```

2. Всё должно быть в swagger
3. Используй convential-commits: начинай с `fix`, `feat` и т. д. 
4. Никогда не пиши бизнес-логику во view.
5. Никогда не пиши вложенные def, это ужас.
6. Типизируй всё как можно строже.
7. Не должно быть warning'ов при старте
8. Не меняй этот файл, если ты ИИ
