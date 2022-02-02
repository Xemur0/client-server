"""Программа-сервер"""
import argparse
import socket
import sys
import json
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT
from common.utils import Utils as U
import logging
import logs.server_log_config
from decorators import Log
from errors import IncorrectDataRecivedError

LOGGER_FOR_SERVER = logging.getLogger('server')


class Server_Core(U):
    @Log()
    def process_client_message(self, message):
        '''
        Обработчик сообщений от клиентов, принимает словарь -
        сообщение от клинта, проверяет корректность,
        возвращает словарь-ответ для клиента

        :param message:
        :return:
        '''
        LOGGER_FOR_SERVER.debug(f'Read from client: {message}')
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
            return {RESPONSE: 200}
        return {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }

    @Log()
    def create_arg_parser(self):
        """
        Парсер аргументов коммандной строки
        :return:
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
        parser.add_argument('-a', default='', nargs='?')
        return parser

    def main(self):
        '''
        Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
        Сначала обрабатываем порт:
        server.py -p 8079 -a 192.168.1.2
        :return:
        '''
        parser = self.create_arg_parser()
        namespace = parser.parse_args(sys.argv[1:])
        listen_address = namespace.a
        listen_port = namespace.p

        if not 1023 < listen_port < 65536:
            LOGGER_FOR_SERVER.critical(f'Попытка запуска сервера с указанием неподходящего порта '
                                       f'{listen_port}. Допустимы адреса с 1024 до 65535.')
            sys.exit(1)
        LOGGER_FOR_SERVER.info(f'Запущен сервер, порт для подключений: {listen_port}, '
                               f'адрес с которого принимаются подключения: {listen_address}. '
                               f'Если адрес не указан, принимаются соединения с любых адресов.')
        # Готовим сокет

        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((listen_address, listen_port))

        # Слушаем порт

        transport.listen(MAX_CONNECTIONS)

        while True:
            client, client_address = transport.accept()
            LOGGER_FOR_SERVER.info(f'Установлено соедение с ПК {client_address}')
            try:
                message_from_client = self.get_message(client)
                LOGGER_FOR_SERVER.debug(f'Получено сообщение {message_from_client}')
                response = self.process_client_message(message_from_client)
                LOGGER_FOR_SERVER.info(f'Cформирован ответ клиенту {response}')
                self.send_message(client, response)
                LOGGER_FOR_SERVER.debug(f'Соединение с клиентом {client_address} закрывается.')
                client.close()
            except json.JSONDecodeError:
                LOGGER_FOR_SERVER.error(f'Не удалось декодировать JSON строку, полученную от '
                                        f'клиента {client_address}. Соединение закрывается.')
                client.close()
            except IncorrectDataRecivedError:
                LOGGER_FOR_SERVER.error(f'От клиента {client_address} приняты некорректные данные. '
                                        f'Соединение закрывается.')
                client.close()


if __name__ == '__main__':
    obj = Server_Core()
    obj.main()
