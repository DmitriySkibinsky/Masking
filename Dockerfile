# Базовый образ Python
FROM python:3.9-slim

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование остальных файлов
COPY . .

# Открытие порта, на котором работает Flask
EXPOSE 5000

# Команда для запуска приложения
CMD ["python", "app.py"]