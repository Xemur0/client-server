import socket
import sys
import logging


if sys.argv[0].find('client') == -1:
    LOGGER = logging.getLogger('server')
else:
    LOGGER = logging.getLogger('client')


class Log:
    def __call__(self, func_to_log):
        def log_saver(*args, **kwargs):
            LOGGER.debug(f'Была вызвана функция {func_to_log.__name__} '
                         f'c параметрами {args} , {kwargs}. '
                         f'Вызов из модуля {func_to_log.__module__}')
            ret = func_to_log(*args, **kwargs)
            return ret
        return log_saver


def login_required(func):
    """
    Декоратор, проверяющий, что клиент авторизован на сервере.
    Проверяет, что передаваемый объект сокета находится в
    списке авторизованных клиентов.
    За исключением передачи словаря-запроса
    на авторизацию. Если клиент не авторизован,
    генерирует исключение TypeError
    """
    def checker(*args, **kwargs):
        """
        Проверка, что первый аргумент - экземпляр MessageProcessor
        """

        from server.core import MessageProcessor
        from common.variables import ACTION, PRESENCE
        if isinstance(args[0], MessageProcessor):
            found = False
            for arg in args:
                if isinstance(arg, socket.socket):
                    for client in args[0].names:
                        if args[0].names[client] == arg:
                            found = True
            for arg in args:
                if isinstance(arg, dict):
                    if ACTION in arg and arg[ACTION] == PRESENCE:
                        found = True
            if not found:
                raise TypeError
        return func(*args, **kwargs)

    return checker
