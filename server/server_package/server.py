import os
import logging
import configparser
import argparse
import sys

sys.path.insert(0, f'../common')
sys.path.insert(0, f'../logs')
sys.path.insert(0, f'../server_package')

from common.decorators import Log
from common.variables import DEFAULT_PORT
from server_package.core import MessageProcessor
from server_package.database import ServerStorage
from server_package.main_window import MainWindow



from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt


LOGGER_FOR_SERVER = logging.getLogger('server')


@Log()
def arg_parser(default_port, default_address):
    """Парсер аргументов коммандной строки."""
    LOGGER_FOR_SERVER.debug(
        f'Инициализация парсера аргументов коммандной строки: {sys.argv}')
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=default_port, type=int, nargs='?')
    parser.add_argument('-a', default=default_address, nargs='?')
    parser.add_argument('--no_gui', action='store_true')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    gui_flag = namespace.no_gui
    LOGGER_FOR_SERVER.debug('Аргументы успешно загружены.')
    return listen_address, listen_port, gui_flag


@Log()
def config_load():
    """Парсер конфигурационного ini файла."""
    config = configparser.ConfigParser()
    dir_path = os.getcwd()
    config.read(f"{dir_path}/{'server.ini'}")
    if 'SETTINGS' in config:
        return config
    else:
        config.add_section('SETTINGS')
        config.set('SETTINGS', 'Default_port', str(DEFAULT_PORT))
        config.set('SETTINGS', 'Listen_Address', '')
        config.set('SETTINGS', 'Database_path', '')
        config.set('SETTINGS', 'Database_file', 'server_database.db3')
        return config


@Log()
def main():
    """Основная функция"""
    config = config_load()
    listen_address, listen_port, gui_flag = arg_parser(
        config['SETTINGS']['Default_port'], config['SETTINGS']
        ['Listen_Address'])

    database = ServerStorage(
        os.path.join(
            config['SETTINGS']['Database_path'],
            config['SETTINGS']['Database_file'],
        ))

    server = MessageProcessor(listen_address, listen_port, database)
    server.daemon = True
    server.start()

    if gui_flag:
        while True:
            command = input('Введите exit для завершения работы сервера.')
            if command == 'exit':
                server.running = False
                server.join()
                break

    else:

        server_app = QApplication(sys.argv)
        server_app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
        main_window = MainWindow(database, server, config)

        server_app.exec_()

        server.running = False


if __name__ == '__main__':
    main()
