**Благотворительный проект QR-кот**

# Работа с Alembic

Alembic — это инструмент для управления миграциями базы данных в проектах на SQLAlchemy. Он позволяет отслеживать изменения в моделях базы данных и применять их с помощью миграций.

## 1. Установка Alembic

pip install alembic

## 2. Инициализация Alembic

alembic init alembic

## 3. Создание миграции

alembic revision --autogenerate -m "Описание изменений"

## 4. Применение миграции

alembic upgrade head

## 5. Откат миграции

alembic downgrade -1

## 6. Просмотр текущего состояния миграций

alembic current

## 7. Просмотр истории миграций

alembic history

## 8. Просмотр всех возможных команд Alembic

alembic --help