import logging
import os
import sys
import threading
import select
import socket
import json

import hmac
import binascii


from common.decorators import login_required
from common.descriptors import Port
from common.utils import get_message, send_message
from common.variables import MAX_CONNECTIONS, DESTINATION, SENDER, ACTION, \
    PRESENCE, TIME, USER, MESSAGE, MESSAGE_TEXT, RESPONSE_200, RESPONSE_400, \
    ERROR, ACCOUNT_NAME, EXIT, GET_CONTACTS, LIST_INFO, RESPONSE_202, \
    ADD_CONTACT, REMOVE_CONTACT, USERS_REQUEST, PUBLIC_KEY_REQUEST, \
    RESPONSE_511, DATA, RESPONSE, PUBLIC_KEY, RESPONSE_205

logger_server = logging.getLogger('server')


class MessageProcessor(threading.Thread):
    """
    Основной класс сервера. Принимает содинения, словари - пакеты
    от клиентов, обрабатывает поступающие сообщения.
    Работает в качестве отдельного потока.
    """
    port = Port()

    def __init__(self, listen_address, listen_port, database):
        """
        Параматеры подключения
        :param listen_address:
        :param listen_port:
        :param database:
        """
        self.listen_address = listen_address
        self.listen_port = listen_port

        self.database = database

        self.sock = None

        self.clients = []

        self.listen_sockets = None
        self.error_sockets = None

        self.running = True
        self.names = dict()
        super().__init__()

    def run(self):
        """Метод основной цикл потока."""
        self.init_socket()

        while self.running:
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                logger_server.info(f'Установлено соедение с ПК '
                                   f'{client_address}')
                client.settimeout(5)
                self.clients.append(client)

            recv_data_lst = []

            try:
                if self.clients:
                    recv_data_lst, self.listen_sockets, self.error_sockets = \
                        select.select(self.clients, self.clients, [], 0)
            except OSError as err:
                logger_server.error(f'Ошибка работы с сокетами: {err.errno}')

            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process_client_message(
                            get_message(client_with_message),
                            client_with_message)
                    except (OSError, json.JSONDecodeError, TypeError) as err:
                        logger_server.debug(f'Getting data from '
                                            f'client exception.', exc_info=err)
                        self.remove_client(client_with_message)

    def remove_client(self, client):
        """
        Метод обработчик клиента с которым прервана связь.
        Ищет клиента и удаляет его из списков и базы:
        """
        logger_server.info(f'Клиент {client.getpeername()} '
                           f'отключился от сервера.')
        for name in self.names:
            if self.names[name] == client:
                self.database.user_logout(name)
                del self.names[name]
                break
        self.clients.remove(client)
        client.close()

    def init_socket(self):
        """Метод инициализатор сокета."""
        logger_server.info(
            f'Запущен сервер, порт для подключений: {self.listen_port} , '
            f'адрес с которого принимаются подключения: '
            f'{self.listen_address}. Если адрес не указан, '
            f'принимаются соединения с любых адресов.')
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.listen_address, self.listen_port))
        transport.settimeout(0.5)

        self.sock = transport
        self.sock.listen(MAX_CONNECTIONS)

    def process_message(self, message):
        """Метод отправки сообщения клиенту."""
        if message[DESTINATION] in self.names and \
                self.names[message[DESTINATION]] in self.listen_sockets:
            try:
                send_message(self.names[message[DESTINATION]], message)
                logger_server.info(
                    f'Отправлено сообщение '
                    f'пользователю {message[DESTINATION]} '
                    f'от пользователя {message[SENDER]}.')
            except OSError:
                self.remove_client(message[DESTINATION])
        elif message[DESTINATION] \
                in self.names \
                and self.names[message[DESTINATION]] \
                not in self.listen_sockets:
            logger_server.error(
                f'Связь с клиентом {message[DESTINATION]} была потеряна. '
                f'Соединение закрыто, доставка невозможна.')
            self.remove_client(self.names[message[DESTINATION]])
        else:
            logger_server.error(
                f'Пользователь {message[DESTINATION]} не зарегистрирован '
                f'на сервере, отправка сообщения невозможна.')

    @login_required
    def process_client_message(self, message, client):
        """Метод отбработчик поступающих сообщений."""
        logger_server.debug(f'Разбор сообщения от клиента : {message}')
        if ACTION in message and message[ACTION] == PRESENCE and TIME \
                in message and USER in message:
            self.autorize_user(message, client)

        elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION \
                in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message \
                and self.names[message[SENDER]] == client:
            if message[DESTINATION] in self.names:
                self.database.process_message(
                    message[SENDER], message[DESTINATION])
                self.process_message(message)
                try:
                    send_message(client, RESPONSE_200)
                except OSError:
                    self.remove_client(client)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Пользователь не зарегистрирован на сервере.'
                try:
                    send_message(client, response)
                except OSError:
                    pass
            return

        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME \
                in message \
                and self.names[message[ACCOUNT_NAME]] == client:
            self.remove_client(client)

        elif ACTION in message and message[ACTION] == GET_CONTACTS and USER \
                in message and \
                self.names[message[USER]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = self.database.get_contacts(message[USER])
            try:
                send_message(client, response)
            except OSError:
                self.remove_client(client)

        elif ACTION in message and message[ACTION] == ADD_CONTACT \
                and ACCOUNT_NAME in message and USER in message \
                and self.names[message[USER]] == client:
            self.database.add_contact(message[USER], message[ACCOUNT_NAME])
            try:
                send_message(client, RESPONSE_200)
            except OSError:
                self.remove_client(client)

        elif ACTION in message and message[ACTION] == REMOVE_CONTACT \
                and ACCOUNT_NAME in message and USER in message \
                and self.names[message[USER]] == client:
            self.database.remove_contact(message[USER], message[ACCOUNT_NAME])
            try:
                send_message(client, RESPONSE_200)
            except OSError:
                self.remove_client(client)

        elif ACTION in message and message[ACTION] == USERS_REQUEST \
                and ACCOUNT_NAME in message \
                and self.names[message[ACCOUNT_NAME]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = [user[0]
                                   for user in self.database.users_list()]
            try:
                send_message(client, response)
            except OSError:
                self.remove_client(client)

        elif ACTION in message and message[ACTION] == PUBLIC_KEY_REQUEST \
                and ACCOUNT_NAME in message:
            response = RESPONSE_511
            response[DATA] = self.database.get_pubkey(message[ACCOUNT_NAME])

            if response[DATA]:
                try:
                    send_message(client, response)
                except OSError:
                    self.remove_client(client)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Нет публичного ключа ' \
                                  'для данного пользователя'
                try:
                    send_message(client, response)
                except OSError:
                    self.remove_client(client)

        else:
            response = RESPONSE_400
            response[ERROR] = 'Запрос некорректен.'
            try:
                send_message(client, response)
            except OSError:
                self.remove_client(client)

    def autorize_user(self, message, sock):
        """Метод реализующий авторизцию пользователей."""
        logger_server.debug(f'Start auth process for {message[USER]}')
        if message[USER][ACCOUNT_NAME] in self.names.keys():
            response = RESPONSE_400
            response[ERROR] = 'Имя пользователя уже занято.'
            try:
                logger_server.debug(f'Username busy, sending {response}')
                send_message(sock, response)
            except OSError:
                logger_server.debug('OS Error')
                pass
            self.clients.remove(sock)
            sock.close()
        elif not self.database.check_user(message[USER][ACCOUNT_NAME]):
            response = RESPONSE_400
            response[ERROR] = 'Пользователь не зарегистрирован.'
            try:
                logger_server.debug(f'Unknown username, sending {response}')
                send_message(sock, response)
            except OSError:
                pass
            self.clients.remove(sock)
            sock.close()
        else:
            logger_server.debug('Correct username, starting passwd check.')
            message_auth = RESPONSE_511
            random_str = binascii.hexlify(os.urandom(64))
            message_auth[DATA] = random_str.decode('ascii')
            hash_info = hmac.new(self.database.get_hash(
                message[USER][ACCOUNT_NAME]), random_str, 'MD5')
            digest = hash_info.digest()
            logger_server.debug(f'Auth message = {message_auth}')
            try:
                send_message(sock, message_auth)
                ans = get_message(sock)
            except OSError as err:
                logger_server.debug('Error in auth, data:', exc_info=err)
                sock.close()
                return
            client_digest = binascii.a2b_base64(ans[DATA])
            if RESPONSE in ans and ans[RESPONSE] == 511 \
                    and hmac.compare_digest(
                    digest, client_digest):
                self.names[message[USER][ACCOUNT_NAME]] = sock
                client_ip, client_port = sock.getpeername()
                try:
                    send_message(sock, RESPONSE_200)
                except OSError:
                    self.remove_client(message[USER][ACCOUNT_NAME])
                self.database.user_login(
                    message[USER][ACCOUNT_NAME],
                    client_ip,
                    client_port,
                    message[USER][PUBLIC_KEY])
            else:
                response = RESPONSE_400
                response[ERROR] = 'Неверный пароль.'
                try:
                    send_message(sock, response)
                except OSError:
                    pass
                self.clients.remove(sock)
                sock.close()

    def service_update_lists(self):
        """Метод реализующий отправки сервисного сообщения 205 клиентам."""
        for client in self.names:
            try:
                send_message(self.names[client], RESPONSE_205)
            except OSError:
                self.remove_client(self.names[client])
