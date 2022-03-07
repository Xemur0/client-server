import binascii
import hashlib
import hmac
import json
import logging
from json import JSONDecodeError
from socket import socket, AF_INET, SOCK_STREAM
import time
import threading
from PyQt5.QtCore import pyqtSignal, QObject
from common.errors import ServerError
from common.utils import send_message, get_message
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, PUBLIC_KEY, RESPONSE, ERROR, DATA, RESPONSE_511, MESSAGE, MESSAGE_TEXT, SENDER, DESTINATION, GET_CONTACTS, LIST_INFO, \
    USERS_REQUEST, PUBLIC_KEY_REQUEST, ADD_CONTACT, REMOVE_CONTACT, EXIT

LOGGER_FOR_CLIENT = logging.getLogger('client')
socket_lock = threading.Lock()


class ClientTransport(threading.Thread, QObject):
    new_message = pyqtSignal(dict)
    connection_lost = pyqtSignal()
    message_205 = pyqtSignal()

    def __init__(self, port, ip_address, database, username, passwd, keys):
        threading.Thread.__init__(self)
        QObject.__init__(self)
        self.database = database
        self.username = username
        self.password = passwd
        self.transport = None
        self.keys = keys
        self.connection_init(port, ip_address)
        try:
            self.user_list_update()
            self.contacts_list_update()
        except OSError as err:
            if err.errno:
                LOGGER_FOR_CLIENT.critical(f'Потеряно соединение с сервером.')
                raise ServerError('Потеряно соединение с сервером!')
            LOGGER_FOR_CLIENT.error(
                'Timeout соединения при обновлении списков пользователей.')
        except json.JSONDecodeError:
            LOGGER_FOR_CLIENT.critical(f'Потеряно соединение с сервером.')
            raise ServerError('Потеряно соединение с сервером!')
        self.running = True

    def connection_init(self, port, ip):
        """
        Метод отвечающий за устанновку соединения с сервером.
        """
        self.transport = socket(AF_INET, SOCK_STREAM)
        self.transport.settimeout(5)

        connected = False
        for i in range(5):
            LOGGER_FOR_CLIENT.info(f'Попытка подключения №{i + 1}')
            try:
                self.transport.connect((ip, port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connected = True
                LOGGER_FOR_CLIENT.debug("Connection established.")
                break
            time.sleep(1)

        if not connected:
            LOGGER_FOR_CLIENT.critical('Не удалось установить соединение с сервером')
            raise ServerError('Не удалось установить соединение с сервером')

        LOGGER_FOR_CLIENT.debug('Starting auth dialog.')

        passwd_bytes = self.password.encode('utf-8')
        salt = self.username.lower().encode('utf-8')
        passwd_hash = hashlib.pbkdf2_hmac('sha512', passwd_bytes, salt, 10000)
        passwd_hash_string = binascii.hexlify(passwd_hash)

        LOGGER_FOR_CLIENT.debug(f'Passwd hash ready: {passwd_hash_string}')

        pubkey = self.keys.publickey().export_key().decode('ascii')

        with socket_lock:
            presense = {
                ACTION: PRESENCE,
                TIME: time.time(),
                USER: {
                    ACCOUNT_NAME: self.username,
                    PUBLIC_KEY: pubkey
                }
            }
            LOGGER_FOR_CLIENT.debug(f"Presense message = {presense}")

            try:
                send_message(self.transport, presense)
                ans = get_message(self.transport)
                LOGGER_FOR_CLIENT.debug(f'Server response = {ans}.')

                if RESPONSE in ans:
                    if ans[RESPONSE] == 400:
                        raise ServerError(ans[ERROR])
                    elif ans[RESPONSE] == 511:
                        ans_data = ans[DATA]
                        hash = hmac.new(passwd_hash_string, ans_data.encode('utf-8'), 'MD5')
                        digest = hash.digest()
                        my_ans = RESPONSE_511
                        my_ans[DATA] = binascii.b2a_base64(
                            digest).decode('ascii')
                        send_message(self.transport, my_ans)
                        self.process_server_ans(get_message(self.transport))
            except (OSError, JSONDecodeError) as err:
                LOGGER_FOR_CLIENT.debug(f'Connection error.', exc_info=err)
                raise ServerError('Сбой соединения в процессе авторизации.')

    def process_server_ans(self, message):
        LOGGER_FOR_CLIENT.debug(f'Разбор сообщения от сервера: {message}')

        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return
            elif message[RESPONSE] == 400:
                raise ServerError(f'{message[ERROR]}')
            elif message[RESPONSE] == 205:
                self.user_list_update()
                self.contacts_list_update()
                self.message_205.emit()
            else:
                LOGGER_FOR_CLIENT.error(
                    f'Принят неизвестный код подтверждения {message[RESPONSE]}')

        elif ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                and MESSAGE_TEXT in message and message[DESTINATION] == self.username:
            LOGGER_FOR_CLIENT.debug(
                f'Получено сообщение от пользователя {message[SENDER]}:{message[MESSAGE_TEXT]}')
            self.new_message.emit(message)

    def contacts_list_update(self):
        self.database.contacts_clear()
        LOGGER_FOR_CLIENT.debug(f'Запрос контакт листа для пользователся {self.name}')
        req = {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            USER: self.username
        }
        LOGGER_FOR_CLIENT.debug(f'Сформирован запрос {req}')
        with socket_lock:
            send_message(self.transport, req)
            ans = get_message(self.transport)
        LOGGER_FOR_CLIENT.debug(f'Получен ответ {ans}')
        if RESPONSE in ans and ans[RESPONSE] == 202:
            for contact in ans[LIST_INFO]:
                self.database.add_contact(contact)
        else:
            LOGGER_FOR_CLIENT.error('Не удалось обновить список контактов.')

    def user_list_update(self):
        LOGGER_FOR_CLIENT.debug(f'Запрос списка известных пользователей {self.username}')
        req = {
            ACTION: USERS_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        with socket_lock:
            send_message(self.transport, req)
            ans = get_message(self.transport)
        if RESPONSE in ans and ans[RESPONSE] == 202:
            self.database.add_users(ans[LIST_INFO])
        else:
            LOGGER_FOR_CLIENT.error('Не удалось обновить список известных пользователей.')

    def key_request(self, user):
        """
        Метод запрашивающий с сервера публичный ключ пользователя.
        """
        LOGGER_FOR_CLIENT.debug(f'Запрос публичного ключа для {user}')
        req = {
            ACTION: PUBLIC_KEY_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: user
        }
        with socket_lock:
            send_message(self.transport, req)
            ans = get_message(self.transport)
        if RESPONSE in ans and ans[RESPONSE] == 511:
            return ans[DATA]
        else:
            LOGGER_FOR_CLIENT.error(f'Не удалось получить ключ собеседника{user}.')

    def add_contact(self, contact):
        """
        Метод отправляющий на сервер сведения о добавлении контакта.
        """
        LOGGER_FOR_CLIENT.debug(f'Создание контакта {contact}')
        req = {
            ACTION: ADD_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            send_message(self.transport, req)
            self.process_server_ans(get_message(self.transport))

    def remove_contact(self, contact):
        """
        Метод отправляющий на сервер сведения о удалении контакта.
        """
        LOGGER_FOR_CLIENT.debug(f'Удаление контакта {contact}')
        req = {
            ACTION: REMOVE_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            send_message(self.transport, req)
            self.process_server_ans(get_message(self.transport))

    def transport_shutdown(self):
        """
        Метод уведомляющий сервер о завершении работы клиента.
        """
        self.running = False
        message = {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        with socket_lock:
            try:
                send_message(self.transport, message)
            except OSError:
                pass
        LOGGER_FOR_CLIENT.debug('Транспорт завершает работу.')
        time.sleep(0.5)

    def send_message(self, to, message):
        """
        Метод отправляющий на сервер сообщения для пользователя.
        """
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.username,
            DESTINATION: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        LOGGER_FOR_CLIENT.debug(f'Сформирован словарь сообщения: {message_dict}')
        with socket_lock:
            send_message(self.transport, message_dict)
            self.process_server_ans(get_message(self.transport))
            LOGGER_FOR_CLIENT.info(f'Отправлено сообщение для пользователя {to}')

    def run(self):
        """
        Метод содержащий основной цикл работы транспортного потока.
        """
        LOGGER_FOR_CLIENT.debug('Запущен процесс - приёмник собщений с сервера.')
        while self.running:
            time.sleep(1)
            message = None
            with socket_lock:
                try:
                    self.transport.settimeout(0.5)
                    message = get_message(self.transport)
                except OSError as err:
                    if err.errno:
                        LOGGER_FOR_CLIENT.critical(f'Потеряно соединение с сервером.')
                        self.running = False
                        self.connection_lost.emit()
                except (ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError, TypeError):
                    LOGGER_FOR_CLIENT.debug(f'Потеряно соединение с сервером.')
                    self.running = False
                    self.connection_lost.emit()
                finally:
                    self.transport.settimeout(5)
            if message:
                LOGGER_FOR_CLIENT.debug(f'Принято сообщение с сервера: {message}')
                self.process_server_ans(message)
