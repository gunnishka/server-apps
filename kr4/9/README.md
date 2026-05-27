# Задание 9.1 - Миграции Alembic

## Установка

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Выполненные требования

1. ✓ Установлена Alembic и SQLite драйвер
2. ✓ Alembic инициализирован в проекте FastAPI
3. ✓ Создана модель Product с полями: id, title, price, count
4. ✓ Сгенерирована первая миграция (создание таблицы)
5. ✓ Применена первая миграция и добавлены 2 записи
6. ✓ Добавлено поле description (not null) к Product
7. ✓ Сгенерирована вторая миграция с изменениями
8. ✓ Применена вторая миграция

## Проверка

Просмотр истории миграций:
```bash
alembic history
```

Просмотр текущей версии:
```bash
alembic current
```

## Структура

- `app/database.py` - модель Product с SQLAlchemy
- `alembic/` - директория с миграциями
- `alembic/versions/` - файлы миграций:
  - `daf23b426992_create_product_table.py` - создание таблицы
  - `1bea4dc49573_add_description_field_to_product.py` - добавление поля description
- `products.db` - SQLite база данных
