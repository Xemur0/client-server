import sys
import logging
import logs.client_log_config
import logs.server_log_config


if sys.argv[0].find('client') == -1:
    LOGGER = logging.getLogger('server')
else:
    LOGGER = logging.getLogger('client')


class Log:
    def __call__(self, func_to_log):
        def log_saver(*args, **kwargs):
            LOGGER.debug(f'Была вызвана функция {func_to_log.__name__} c параметрами {args} , {kwargs}. Вызов из модуля {func_to_log.__module__}')
            ret = func_to_log(*args, **kwargs)
            return ret
        return log_saver
