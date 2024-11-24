# Используем официальный образ Python 3.12
FROM python:3.12-slim

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости в контейнер
COPY requirements.txt /app/

# Обновляем apt и устанавливаем зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove -y gcc \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копируем всё содержимое проекта
COPY . /app/

WORKDIR /app/repository

# Задаём команду по умолчанию
CMD ["python" "start.py"]
