import time
import os
import logging
from dotenv import load_dotenv

from telegram import Bot

from exceptions import check_get_api, exception_error, exception_critical


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
    return response.json()


def check_response(response):
    """ Проверка ожидаемого ответа. """
    homeworks = response.get('homeworks')

    if not 'homeworks' in response.keys():
        raise exception_error('Некорректный запрашеваемый элемент по ключу homeworks')

    if len(homeworks) == 0:
        return False

    return homeworks


def check_status(last_review):
    """ Если в из API пришел статус. """
    status = last_review.get('status')
    if not status:
        raise exception_error('Недокументированный статус домашней работы')
        
    return status


def parse_status(homework):
    # Проверить homework_name и HOMEWORK_STATUSES
    status = check_status(homework)

    homework_name = homework.get('homework_name')
    verdict = HOMEWORK_STATUSES.get(status)

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    if not PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        raise exception_critical('Отсуствует токен!')


def get_last_review(all_review):
    last_review = all_review[len(all_review) - 1]
    return last_review


def main():
    """ В первый раз присылает статус моей работы, если статус изменился, присылает новое сообщение, если нет, ничего не присылает """
    # int(time.time())
    # 1634074965
    current_timestamp = 1634074965
    bot = Bot(token=TELEGRAM_TOKEN)

    while True:
        try:
            check_tokens()

            response = get_api_answer(current_timestamp)

            print(response)

            homeworks = check_response(response)
            if homeworks:
                last_review = get_last_review(homeworks)

                message = parse_status(last_review)
                send_message(bot, message)
                logging.debug('Отсутствие в ответе новых статусов')

            current_timestamp = response.get('current_date', current_timestamp)

            time.sleep(10)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
            time.sleep(RETRY_TIME)

if __name__ == '__main__':
    main()
