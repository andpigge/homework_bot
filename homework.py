import time
import os
import logging
from dotenv import load_dotenv
import requests

from telegram import Bot

from exceptions import (
    exception_error,
    exception_critical,
    exception_warning,
    exception_key_error,
    exception_type_error
)


load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправка в телеграмм бот сообщения."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)

        name_bot = bot['username']

        logging.info(
            f'Сообщение успешно отправленно на телеграмм бот: {name_bot}!'
        )
    except Exception as error:
        if error == 'Unauthorized':
            logging.critical(
                f'{error}. Некорректный токен или токен отсуствует!'
            )
        else:
            logging.error(
                f'{error}. Не удалось отправить сообщение в телеграмм бот!'
            )


def check_get_api(endpoint, headers, params):
    """Проверка на положительный и отрицательные запросы к API."""
    response = requests.get(endpoint, headers=headers, params=params)

    try:
        if response.status_code < 400:
            logging.info(f'Запрос на адрес {endpoint} прошел успешно!')
            return response
        raise exception_error(
            f'{response.status_code}.'
            f'Запрос на адрес {endpoint} завершился с ошибкой!'
        )
    except Exception:
        raise exception_error(
            f'{response.status_code}.'
            f'Запрос на адрес {endpoint} завершился с ошибкой!'
        )


def get_api_answer(current_timestamp):
    """Проверка что запрос прошел успешно."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}

    response = check_get_api(
        ENDPOINT,
        headers=HEADERS,
        params=params
    )
    return response.json()


def check_response(response):
    """
    Проверка что запрос соотвествует ожидаемому.
    и у него есть ключ homeworks.
    """
    if not isinstance(response, dict):
        raise exception_type_error('Ожидается в присланном ответе коллекцию!')

    if 'homeworks' not in response:
        raise exception_key_error(
            'Некорректный запрашеваемый элемент по ключу homeworks!'
        )

    homeworks = response.get('homeworks')

    if not isinstance(homeworks, list):
        raise exception_type_error('Ожидается под ключем homeworks список!')

    return homeworks


def parse_status(homework):
    """
    Из полученной работы получить статус,.
    из статуса сформировать и вернуть строку.
    """
    status = homework.get('status')

    if not status:
        raise exception_error('Недокументированный статус домашней работы!')

    if 'homework_name' not in homework:
        raise exception_key_error(
            'Некорректный запрашеваемый элемент по ключу homework_name!'
        )

    homework_name = homework.get('homework_name')

    if status not in HOMEWORK_STATUSES:
        raise exception_key_error('Статусы работ не определены!')

    verdict = HOMEWORK_STATUSES.get(status)

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверить существуют ли переменные окружения."""
    if all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)) == False:
        return False
    return True


def main():
    """
    Получить из API статус домашней работы,.
    и отправить его в телеграмм бот.
    """
    if not check_tokens():
        exception_critical(
            "Отсутствует обязательная переменная окружения!"
        )
        return

    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    count = 0

    while True:
        try:
            response = get_api_answer(current_timestamp)

            homeworks = check_response(response)

            if homeworks:
                for homework in homeworks:
                    message = parse_status(homework)
                    send_message(bot, message)

            logging.debug('Отсутствие в ответе новых статусов!')

            current_timestamp = response.get('current_date', current_timestamp)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            exception_warning(message)

            if count == 0:
                count = 1
                send_message(bot, message)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename='homework.log',
        filemode='w',
        format=(
            '%(asctime)s, %(levelname)s, %(message)s, %(funcName)s, %(lineno)d, %(name)s'
        ),
        encoding='utf=8'
    )

    main()
