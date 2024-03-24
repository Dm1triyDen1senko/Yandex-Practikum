import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv


load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TOKENS = ['PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID']

MAX_LOG_FILE_SIZE = 1024 * 1024 * 5
RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
payload = {'from_date': 0}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

CONNECTION_ERROR = (
    "Ошибка при выполнении запроса к API: {}"
    "Endpoint: {url} Headers: {headers} Params: {params}"
)

RESPONSE_CODE_ERROR = (
    "Получен неверный статус ответа: {}"
    "Endpoint: {url} Headers: {headers} Params: {params}"
)

RESPONSE_ERROR = (
    "Неверный ответ API: {}: {}"
    "Endpoint: {url} Headers: {headers} Params: {params}"
)

TOKEN_ERROR = "Беда с токенами окружения: {}"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s]: %(message)s %(name)s',
    handlers=[
        RotatingFileHandler(
            filename=__file__ + '.log',
            maxBytes=MAX_LOG_FILE_SIZE,
            encoding='UTF-8',
        ),
        logging.StreamHandler(sys.stdout)
    ]
)


def check_tokens():
    """Проверка доступности переменных окружения."""
    missing_tokens = [token for token in TOKENS if globals()[token] is None]
    if missing_tokens:
        logging.critical(TOKEN_ERROR.format(missing_tokens))
        raise ValueError(TOKEN_ERROR.format(missing_tokens))


def send_message(bot, message):
    """Отправка пользователю сообщения в зависимости от статуса проверки ДЗ."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Успешная отправка сообщения в чат с пользователем.')
        return True
    except telegram.TelegramError as error:
        logging.exception(
            f'Возникла ошибка отправки: {error} сообщения: {message}'
        )
        return False


def get_api_answer(timestamp):
    """Проведение запроса к API Практикум.Домашки."""
    request_params = dict(
        url=ENDPOINT, headers=HEADERS, params={'from_date': timestamp}
    )
    try:
        response = requests.get(**request_params)
    except requests.RequestException as error:
        raise ConnectionError(
            CONNECTION_ERROR.format(error, **request_params)
        )
    if response.status_code != HTTPStatus.OK:
        raise ValueError(
            RESPONSE_CODE_ERROR.format(response.status_code, **request_params)
        )
    response = response.json()
    for item in ['code', 'error']:
        if item in response:
            raise ValueError(
                RESPONSE_ERROR.format(item, response[item], **request_params)
            )
    return response


def check_response(response):
    """Проверка ответа API на соответствие документации Практикум.Домашки."""
    if not isinstance(response, dict):
        raise TypeError('Ответ API не соответствует ожидаемому формату.')
    if (homeworks := response.get('homeworks')) is None:
        raise KeyError('Homeworks не найден в ответе.')
    homeworks = response['homeworks']
    if not isinstance(homeworks, list):
        raise TypeError('Homeworks не является списком.')
    return homeworks


def parse_status(homework):
    """Извлечение статуса работы из информации о конкретной домашней работе."""
    if (homework_name := homework.get('homework_name')) is None:
        raise KeyError('В ответе API не найдено название домашки.')
    if 'status' not in homework:
        raise KeyError('Домашка не содержит информацию о статусе.')
    status = homework.get('status')
    if status not in HOMEWORK_VERDICTS:
        raise KeyError(
            'Ответ API содержит неизвестный статус ДЗ'
            'или не содержит статуса вовсе.'
        )

    homework_name = homework.get('homework_name')
    verdict = HOMEWORK_VERDICTS.get(status)

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Описание основной логики работы программы."""
    check_tokens()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    previous_message = None

    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)

            if not homeworks:
                continue

            message = parse_status(homeworks[0])
            if message != previous_message and send_message(bot, message):
                timestamp = response.get('current_date', timestamp)
                previous_message = message
            else:
                logging.debug('Нет обновлений.')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            if message != previous_message and send_message(bot, message):
                previous_message = message
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
