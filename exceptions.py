import logging


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


class exception_warning(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
            logging.warning(self.message)
        else:
            self.message = None
            logging.exception('Ошибка')


class exception_key_error(KeyError):
    def __init__(self, *args):
        if args:
            self.message = args[0]
            logging.error(self.message)
        else:
            self.message = None
            logging.exception('Ошибка')


class exception_type_error(TypeError):
    def __init__(self, *args):
        if args:
            self.message = args[0]
            logging.error(self.message)
        else:
            self.message = None
            logging.exception('Ошибка')
