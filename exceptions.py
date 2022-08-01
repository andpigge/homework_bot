import requests
from dotenv import load_dotenv
import logging

load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    filename='homework.log',
    filemode='w',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
)

class Exceptions(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'Exceptions, {0} '.format(self.message)
        else:
            return 'Exceptions, ошибка'


def check_get_api(endpoint, headers, params):
    """ Проверка на валидность получения домашнего задания. """
    response = requests.get(endpoint, headers=headers, params=params)

    if response.ok:
        logging.info(f'Запрос на адрес {endpoint} прошел успешно!')
        return response

    try:
        message = response.json()['message']
        code = response.json()['code']
    except Exception:
        logging.error(f'{response.status_code}. Запрос на адрес {endpoint} завершился с ошибкой!')
    else:
        logging.critical(f'{code}: {message}.')
