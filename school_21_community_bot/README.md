# school_21_community_bot_1
[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=ffffff&color=043A6B)](https://www.python.org/)
[![SQLAlchemy](https://img.shields.io/badge/-SQLAlchemy-464646?style=flat&logo=SQLAlchemy%20REST%20Framework&logoColor=ffffff&color=043A6B)](https://www.sqlalchemy.org/)
[![Alembic](https://img.shields.io/badge/-Alembic-464646?style=flat&logo=Alembic&logoColor=ffffff&color=043A6B)](https://alembic.sqlalchemy.org/en/latest/)
[![python-telegram-bot](https://img.shields.io/badge/-python_telegram_bot-464646?style=flat&logo=pythontelegrambot&logoColor=ffffff&color=043A6B)](https://docs.python-telegram-bot.org/en/v21.6/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)

## Описание проекта
Телеграм-бот создан для сбора основной информации о пользователях и автоматической отправки им одноразовой ссылки для приглашения в закрытый чат. После регистрации и заполнения необходимых данных пользователь может начать поиск сотрудников (пиров) по различным критериям, включая роли, уровни квалификации и дополнительные параметры. Результаты поиска можно отфильтровать.

### Шаблон заполнения файла `school_21_community_bot_1/.env`
```
- TELEGRAM_BOT_TOKEN=

- BOT_NAME=

- DATABASE_URL=

- GROUP_ID=

- INVITE_LINK=

- POSTGRES_USER=

- POSTGRES_PASSWORD=

- POSTGRES_DB=

```

#### Запуск проекта локально
- Клонируйте репозиторий и перейдите в папку проекта:
```
git clone git@github.com:Studio-Yandex-Practicum/school_21_community_bot_1.git
```
- Установите и активируйте виртуальное окружение:
```bash
python -m venv venv
```
```bash
source venv/Scripts/activate
```
- Установите зависимости из файла requirements.txt:
```bash
python -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```
- Создать и заполнить файл **.env** в соответствии с рекомендациями
- Применение миграций
```bash
alembic upgrade head 
```
- Запустить проект
```bash
python main.py
```

#### Установка на удалённом сервере

- Выполнить вход на удаленный сервер
- Установить docker:

```bash
   sudo apt install docker.io
   ```

- Установить docker-compose:

``` bash
    sudo apt install docker-compose     
```

или воспользоваться официальной [инструкцией](https://docs.docker.com/compose/install/)

- Находясь в корневой директории проекта, скопировать файл docker-compose.yml на удаленный сервер:

```bash
scp docker-compose.yml <username>@<host>:/home/<username>/
```
- Запустите Docker-compose:

```bash
   sudo docker compose up -d
```
  
- Примените миграции:

```bash
   sudo docker exec school_21_community_bot_1-telegram_bot-1 alembic upgrade head
```

#### Авторы: 

- [Кузнецов Клим](https://github.com/tornitok)

- [Ефимов Станислав](https://github.com/RedCloverfield)

- [Игнатьев Денис](https://github.com/diesel1701-afk)

- [Денисенко Дмитрий](https://github.com/Dm1triyDen1senko)

- [Земцова Елизавета](https://github.com/Elizaveta-u)

- [Завьялова Ульяна](https://github.com/zavjalovaue)
