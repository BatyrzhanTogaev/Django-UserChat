FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Собираем статику (важно до CMD)
RUN python manage.py collectstatic --noinput

# Создаём директорию для статики
RUN mkdir -p /app/staticfiles

# Запускаем через Gunicorn с UvicornWorker
CMD ["gunicorn", "UserChat.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
