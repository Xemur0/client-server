import argparse
import os
import sys
import logging

sys.path.insert(1, f'.../common')
sys.path.insert(1, f'.../logs')
sys.path.insert(1, f'../client_package')

from client_package.database import ClientDatabase
from client_package.main_window import ClientMainWindow
from client_package.start_dialog import UserNameDialog
from client_package.transport import ClientTransport
from common.decorators import Log
from common.errors import ServerError
from common.variables import DEFAULT_IP_ADDRESS, DEFAULT_PORT

from Cryptodome.PublicKey import RSA
from PyQt5.QtWidgets import QApplication, QMessageBox


logger_client = logging.getLogger('client')


@Log()
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    parser.add_argument('-p', '--password', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name
    client_passwd = namespace.password

    if not 1023 < server_port < 65536:
        logger_client.critical(
            f'Попытка запуска клиента '
            f'с неподходящим номером порта: {server_port}. '
            f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
        sys.exit(1)

    return server_address, server_port, client_name, client_passwd


if __name__ == '__main__':

    server_address, server_port, client_name, client_passwd = arg_parser()
    logger_client.debug('Args loaded')

    client_app = QApplication(sys.argv)
    start_dialog = UserNameDialog()
    if not client_name or not client_passwd:
        client_app.exec_()
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            client_passwd = start_dialog.client_passwd.text()
            logger_client.debug(f'Using USERNAME = {client_name}, 'f'PASSWD = '
                                f'{client_passwd}.')
        else:
            sys.exit(0)

    logger_client.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address} , '
        f'порт: {server_port}, имя пользователя: {client_name}')

    dir_path = os.getcwd()
    key_file = os.path.join(dir_path, f'{client_name}.key')
    if not os.path.exists(key_file):
        keys = RSA.generate(2048, os.urandom)
        with open(key_file, 'wb') as key:
            key.write(keys.export_key())
    else:
        with open(key_file, 'rb') as key:
            keys = RSA.import_key(key.read())

    logger_client.debug("Keys sucsessfully loaded.")
    database = ClientDatabase(client_name)

    try:
        transport = ClientTransport(
            server_port,
            server_address,
            database,
            client_name,
            client_passwd,
            keys)
        logger_client.debug("Transport ready.")
    except ServerError as error:
        message = QMessageBox()
        message.critical(start_dialog, 'Ошибка сервера', error.text)
        sys.exit(1)
    transport.setDaemon(True)
    transport.start()

    del start_dialog

    main_window = ClientMainWindow(database, transport, keys)
    main_window.make_connection(transport)
    main_window.setWindowTitle(f'Чат Программа alpha release - {client_name}')
    client_app.exec_()
    transport.transport_shutdown()
    transport.join()
