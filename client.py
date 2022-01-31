"""Программа-клиент"""
import argparse
import sys
import json
import socket
import time
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT
from common.utils import Utils as U
import logging
import logs.client_log_config
from errors import ReqFieldMissingError

LOGGER_FOR_CLIENT = logging.getLogger('client')


class Client_Core(U):
    def create_arg_parser(self):
        """
        Создаём парсер аргументов коммандной строки
        :return:
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
        parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
        return parser

    def create_presence(self, account_name='Guest'):
        '''
        Функция генерирует запрос о присутствии клиента
        :param account_name:
        :return:
        '''
        # {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
        out = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: account_name
            }
        }
        LOGGER_FOR_CLIENT.debug(f'Formed {PRESENCE} message for {account_name}')
        return out

    def process_ans(self, message):
        '''
        Функция разбирает ответ сервера
        :param message:
        :return:
        '''
        LOGGER_FOR_CLIENT.debug(f'Read from server: {message}')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200 : OK'
            return f'400 : {message[ERROR]}'
        raise ValueError

    def main(self):
        '''Загружаем параметы коммандной строки'''
        # client.py 192.168.1.2 8079

        parser = self.create_arg_parser()
        namespace = parser.parse_args(sys.argv[1:])
        server_address = namespace.addr
        server_port = namespace.port

        if not 1023 < server_port < 65536:
            LOGGER_FOR_CLIENT.critical(
                f'Попытка запуска клиента с неподходящим номером порта: {server_port}.'
                f' Допустимы адреса с 1024 до 65535. Клиент завершается.')
            sys.exit(1)

        LOGGER_FOR_CLIENT.info(f'Запущен клиент с парамертами: '
                               f'адрес сервера: {server_address}, порт: {server_port}')
        try:
            transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            transport.connect((server_address, server_port))
            message_to_server = self.create_presence()
            self.send_message(transport, message_to_server)
            answer = self.process_ans(self.get_message(transport))
            LOGGER_FOR_CLIENT.debug(f'Принят ответ от сервера {answer}')
            print(answer)
        except json.JSONDecodeError:
            LOGGER_FOR_CLIENT.error('Не удалось декодировать полученную Json строку.')
        except ReqFieldMissingError as missing_error:
            LOGGER_FOR_CLIENT.error(f'В ответе сервера отсутствует необходимое поле '
                                    f'{missing_error.missing_field}')
        except ConnectionRefusedError:
            LOGGER_FOR_CLIENT.critical(f'Не удалось подключиться к серверу {server_address}:{server_port}, '
                                       f'конечный компьютер отверг запрос на подключение.')


if __name__ == '__main__':
    obj = Client_Core()
    obj.main()
