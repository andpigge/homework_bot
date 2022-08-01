import time
import os
import logging
from dotenv import load_dotenv

from pprint import pprint

from telegram import Bot

from exceptions import check_get_api


load_dotenv()

# Провепка на валидность токенов
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

logging.basicConfig(
    level=logging.DEBUG,
    filename='homework.log',
    filemode='w',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
)

def send_message(bot, message):
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)

        name_bot = bot['username']

        logging.info(f'Сообщение успешно отправленно на телеграмм бот: {name_bot}!')
    except Exception as error:
        if error == 'Unauthorized':
            logging.critical(f'{error}. Некорректный токен или токен отсуствует!!')
        else:
            logging.error(f'{error}. Не удалось отправить сообщение в телеграмм бот!')


def get_api_answer(current_timestamp):
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}

    response = check_get_api(ENDPOINT, headers=HEADERS, params=params)

    if not response:
        return False
    
    return response.json()


def check_response(response):
    """ Проверка ожидаемого ответа. """
    if not response:
        return False

    if not response.get('homeworks'):
        logging.error('Некорректный запрашеваемый элемент по ключу homeworks')
        return False

    return response['homeworks']


def check_status(last_review):
    """ Если в из API пришел статус. """
    try:
        status = last_review['status']
        return status
    except Exception:
        logging.error('Недокументированный статус домашней работы')
        return False


def parse_status(homework):
    # Проверить homework_name и HOMEWORK_STATUSES
    status = check_status(homework)

    if not status:
        return False
    
    homework_name = homework.get('homework_name')
    verdict = HOMEWORK_STATUSES.get(status)

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        return True
    logging.critical('Отсуствует токен!')
    return False


def get_last_review(all_review):
    if len(all_review) == 0:
        return False

    last_review = all_review[len(all_review) - 1]
    return last_review


def main():
    """ В первый раз присылает статус моей работы, если статус изменился, присылает новое сообщение, если нет, ничего не присылает """
    if not check_tokens():
        # Нужно чтобы программа работала, а не прерывалась
        return

    # int(time.time())
    current_timestamp = 1634074965
    bot = Bot(token=TELEGRAM_TOKEN)

    response = get_api_answer(current_timestamp)
    if not response:
        return

    homeworks = check_response(response)
    if not homeworks:
        return

    last_review = get_last_review(homeworks)
    if not last_review:
        return

    status = check_status(last_review)
    if not status:
        return

    while True:
        try:
            time.sleep(10)

            if not check_tokens():
                return

            response = get_api_answer(current_timestamp)
            if not response:
                return

            

            homeworks = check_response(response)
            if not homeworks:
                return

            last_review = get_last_review(homeworks)
            if not last_review:
                return

            message = parse_status(last_review)
            if not message:
                return

            new_status = check_status(last_review)
            if not new_status:
                return

            if status != new_status:
                status = new_status

                send_message(bot, message)
            else:
                logging.debug('Отсутствие в ответе новых статусов')

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            time.sleep(RETRY_TIME)

if __name__ == '__main__':
    main()
