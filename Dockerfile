# Використовуємо базовий образ з Python
FROM python:3.12-slim

# Встановлюємо Poetry
RUN pip install poetry

# Встановлюємо змінну середовища для налаштування Poetry
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо файл конфігурації Poetry та файл блокування залежностей
COPY pyproject.toml poetry.lock /app/

# Встановлюємо залежності проекту
RUN poetry install --no-root

# Копіюємо весь проект в контейнер
COPY . /app

# Визначаємо команду для запуску вашого додатку
CMD ["python", "main.py"]
