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


class exception_critical(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
            logging.critical(self.message)
        else:
            self.message = None
            logging.exception('Ошибка')


class exception_error(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
            logging.error(self.message)
        else:
            self.message = None
            logging.exception('Ошибка')


def check_get_api(endpoint, headers, params):
    """ Проверка на положительный запрос к API. """
    response = requests.get(endpoint, headers=headers, params=params)

    if response.ok:
        logging.info(f'Запрос на адрес {endpoint} прошел успешно!')
        return response

    try:
        message = response.json()['message']
        code = response.json()['code']
    except Exception:
        exception_error(f'{response.status_code}. Запрос на адрес {endpoint} завершился с ошибкой!')
    else:
        exception_critical(logging.critical(f'{code}: {message}.'))
