class exception_critical(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None


class exception_error(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None


class exception_key_error(KeyError):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None


class exception_type_error(TypeError):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None
