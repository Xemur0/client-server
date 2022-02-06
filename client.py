"""Программа-клиент"""
import argparse
import sys
import json
import socket
import time
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, MESSAGE, MESSAGE_TEXT, SENDER
from common.utils import Utils as U
import logging
import logs.client_log_config
from errors import ReqFieldMissingError, ServerError
from decorators import Log

LOGGER_FOR_CLIENT = logging.getLogger('client')


class Client_Core(U):

    def message_from_server(self, message):
        """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
        if ACTION in message and message[ACTION] == MESSAGE and \
                SENDER in message and MESSAGE_TEXT in message:
            print(f'Получено сообщение от пользователя '
                  f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
            LOGGER_FOR_CLIENT.info(f'Получено сообщение от пользователя '
                                   f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
        else:
            LOGGER_FOR_CLIENT.error(f'Получено некорректное сообщение с сервера: {message}')

    @Log()
    def create_arg_parser(self):
        """
        Создаём парсер аргументов коммандной строки
        :return:
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
        parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
        parser.add_argument('-m', '--mode', default='listen', nargs='?')
        parser.add_argument('-n', '--name')
        namespace = parser.parse_args(sys.argv[1:])
        server_address = namespace.addr
        server_port = namespace.port
        client_mode = namespace.mode
        client_name = namespace.name

        # проверим подходящий номер порта
        if not 1023 < server_port < 65536:
            LOGGER_FOR_CLIENT.critical(
                f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
                f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
            sys.exit(1)

        # Проверим допустим ли выбранный режим работы клиента
        if client_mode not in ('listen', 'send'):
            LOGGER_FOR_CLIENT.critical(f'Указан недопустимый режим работы {client_mode}, '
                                       f'допустимые режимы: listen , send')
            sys.exit(1)

        return server_address, server_port, client_mode, client_name

    @Log()
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

    @Log()
    def process_ans(self, message):
        '''
        Функция разбирает ответ сервера
        :param message:
        :return:
        '''
        LOGGER_FOR_CLIENT.debug(f'Разбор приветственного сообщения от сервера: {message}')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200 : OK'
            elif message[RESPONSE] == 400:
                raise ServerError(f'400 : {message[ERROR]}')
        raise ReqFieldMissingError(RESPONSE)

    def create_message(self, sock):
        """Функция запрашивает текст сообщения и возвращает его.
        Так же завершает работу при вводе подобной комманды
        """

        client_name = input('Введите имя пользователя для отправки сообщения: ')
        message = input('Введите сообщение для отправки или \'!!!\' для завершения работы: ')
        if message == '!!!':
            sock.close()
            LOGGER_FOR_CLIENT.info('Завершение работы по команде пользователя.')
            print('Спасибо за использование нашего сервиса!')
            sys.exit(0)
        message_dict = {
            ACTION: MESSAGE,
            TIME: time.time(),
            ACCOUNT_NAME: client_name,
            MESSAGE_TEXT: message
        }
        LOGGER_FOR_CLIENT.debug(f'Сформирован словарь сообщения: {message_dict}')
        return message_dict

    def main(self):
        '''Загружаем параметы коммандной строки'''
        # client.py 192.168.1.2 8079

        server_address, server_port, client_mode, client_name = self.create_arg_parser()

        LOGGER_FOR_CLIENT.info(
            f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
            f'порт: {server_port}, режим работы: {client_mode}')

        # Инициализация сокета и сообщение серверу о нашем появлении
        try:
            transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            transport.connect((server_address, server_port))
            self.send_message(transport, self.create_presence())
            answer = self.process_ans(self.get_message(transport))
            LOGGER_FOR_CLIENT.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
            print(f'Установлено соединение с сервером.')
        except json.JSONDecodeError:
            LOGGER_FOR_CLIENT.error('Не удалось декодировать полученную Json строку.')
            sys.exit(1)
        except ServerError as error:
            LOGGER_FOR_CLIENT.error(f'При установке соединения сервер вернул ошибку: {error.text}')
            sys.exit(1)
        except ReqFieldMissingError as missing_error:
            LOGGER_FOR_CLIENT.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
            sys.exit(1)
        except ConnectionRefusedError:
            LOGGER_FOR_CLIENT.critical(
                f'Не удалось подключиться к серверу {server_address}:{server_port}, '
                f'конечный компьютер отверг запрос на подключение.')
            sys.exit(1)
        else:
            # Если соединение с сервером установлено корректно,
            # начинаем обмен с ним, согласно требуемому режиму.
            # основной цикл прогрммы:
            if client_mode == 'send':
                print('Режим работы - отправка сообщений.')
            else:
                print('Режим работы - приём сообщений.')
            while True:
                # режим работы - отправка сообщений
                if client_mode == 'send':
                    try:
                        self.send_message(transport, self.create_message(transport))
                    except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                        LOGGER_FOR_CLIENT.error(f'Соединение с сервером {server_address} было потеряно.')
                        sys.exit(1)

                # Режим работы приём:
                if client_mode == 'listen':
                    try:
                        self.message_from_server(self.get_message(transport))
                    except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                        LOGGER_FOR_CLIENT.error(f'Соединение с сервером {server_address} было потеряно.')
                        sys.exit(1)


if __name__ == '__main__':
    obj = Client_Core()
    obj.main()
