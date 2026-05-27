# Задание 10.1 и 10.2 - Пользовательская обработка ошибок и валидация

## Установка

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Выполненные требования

### Задание 10.1 - Обработка ошибок

1. ✓ Созданы пользовательские классы исключений:
   - `CustomExceptionA` с status_code 400
   - `CustomExceptionB` с status_code 404

2. ✓ Зарегистрированы обработчики исключений
   - Возвращают соответствующие коды статуса и сообщения об ошибках

3. ✓ Определены модели ответов на ошибки (Pydantic BaseModel)

4. ✓ Реализованы два эндпоинта, вызывающих исключения:
   - `POST /condition-endpoint` - вызывает CustomExceptionA
   - `GET /resource/{resource_id}` - вызывает CustomExceptionB

5. ✓ Протестирована обработка ошибок через отправку запросов

### Задание 10.2 - Валидация данных

1. ✓ Создано приложение FastAPI с эндпоинтом:
   - `POST /validate-user` - принимает JSON с данными пользователя

2. ✓ Определена модель Pydantic User с валидацией:
   - `username: str` - минимум 3 символа
   - `age: int` - должно быть > 18
   - `email: EmailStr` - корректный email
   - `password: str` - 8-16 символов
   - `phone: Optional[str]` - опциональное поле (по умолчанию 'Unknown')

3. ✓ Реализована пользовательская обработка ошибок валидации

4. ✓ Протестирована обработка ошибок валидации

## Запуск

Локальный запуск:
```bash
uvicorn app.main:app --reload
```

Запуск тестов:
```bash
pytest tests/test_main.py -v
```

Все 12 тестов должны пройти успешно.

## API Эндпоинты

### POST /condition-endpoint
Проверяет, положительно ли значение.
```json
{
  "value": 10
}
```

### GET /resource/{resource_id}
Возвращает ресурс если ID <= 100, иначе 404.

### POST /validate-user
Валидирует данные пользователя.
```json
{
  "username": "john_doe",
  "age": 25,
  "email": "john@example.com",
  "password": "secure123",
  "phone": "+1234567890"
}
```

## Структура

- `app/main.py` - основное приложение с эндпоинтами и обработчиками
- `tests/test_main.py` - 12 тестов для проверки функциональности
