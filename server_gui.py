import sys
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QLabel, QTableView, QDialog, QPushButton, \
    QLineEdit, QFileDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt


def create_gui_model(database):
    list_of_users = database.active_users_list()
    list_ = QStandardItemModel()
    list_.setHorizontalHeaderLabels(['Name', 'IP', 'Port', 'Time in'])
    for row in list_of_users:
        user, ip, port, time = row
        user = QStandardItem(user)
        user.setEditable(False)
        ip = QStandardItem(ip)
        ip.setEditable(False)
        port = QStandardItem(port)
        port.setEditable(False)
        time = QStandardItem(str(time.replace(microsecond=0)))
        time.setEditable(False)
        list_.appendRow([user, ip, port, time])

    return list_


def fill_table(database):
    history_list = database.message_history()

    list_info = QStandardItemModel()
    list_info.setHorizontalHeaderLabels(['Name', 'Last seen', 'Messages Out', 'Messages In'])
    for row in history_list:
        name, last_seen, msg_out, msg_in = row
        name = QStandardItem(name)
        name.setEditable(False)

        last_seen = QStandardItem(str(last_seen.replace(microsecond=0)))
        last_seen.setEditable(False)

        msg_out = QStandardItem(str(msg_out))
        msg_out.setEditable(False)

        msg_in = QStandardItem(str(msg_in))
        msg_in.setEditable(False)

        list_info.appendRow([name, last_seen, msg_out, msg_in])

    return list_info


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        exit_btn = QAction('Exit', self)
        exit_btn.setShortcut('Ctrl+Q')
        exit_btn.triggered.connect(qApp.quit)

        self.refresh_button = QAction('Refresh', self)
        self.config_button = QAction('Options', self)
        self.history_button = QAction('History', self)

        self.statusBar()

        self.toolbar = self.addToolBar('Mainbar')
        self.toolbar.addAction(exit_btn)
        self.toolbar.addAction(self.refresh_button)
        self.toolbar.addAction(self.config_button)
        self.toolbar.addAction(self.history_button)

        self.setFixedSize(800, 600)
        self.setWindowTitle('Messaging Server')

        # self.label = QLabel('Connected users:', self)
        # self.label.setFixedSize(240, 75)
        # self.move(10, 30)

        self.connected_clients = QTableView(self)
        self.connected_clients.move(10, 45)
        self.connected_clients.setFixedSize(780, 400)

        self.show()


class HistoryWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Statistic')
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.close_button = QPushButton('Close', self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)

        self.history_list = QTableView(self)
        # self.history_list.move(250, 650)
        self.history_list.setFixedSize(580, 620)

        self.show()


class ConfigurationWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(365, 260)
        self.setWindowTitle('Preferences for Server')

        self.db_path_label = QLabel('Path to file database: ', self)
        self.db_path_label.move(10, 10)
        self.db_path_label.setFixedSize(240, 15)

        self.db_path = QLineEdit(self)
        self.db_path.setFixedSize(250, 20)
        self.db_path.move(10, 30)
        self.db_path.setReadOnly(True)

        self.db_path_button = QPushButton('Browse...', self)
        self.db_path_button.move(275, 28)

        def open_file_dialog():
            global dialog
            dialog = QFileDialog(self)
            path = dialog.getExistingDirectory()
            path = path.replace('/', '\\')
            self.db_path.insert(path)

        self.db_path_button.clicked.connect(open_file_dialog)

        self.db_file_label = QLabel('Name: ', self)
        self.db_file_label.move(10, 68)
        self.db_file_label.setFixedSize(150, 20)

        self.db_file = QLineEdit(self)
        self.db_file.move(200, 66)
        self.db_file.setFixedSize(150, 20)

        self.port_label = QLabel('Port: ', self)
        self.port_label.move(10, 108)
        self.port_label.setFixedSize(180, 15)

        self.port = QLineEdit(self)
        self.port.move(200, 108)
        self.port.setFixedSize(150, 20)

        self.ip_label = QLabel('IP in: ', self)
        self.ip_label.move(10, 148)
        self.ip_label.setFixedSize(180, 15)

        self.ip_label_note = QLabel('Empty - for everyone connect', self)
        self.ip_label_note.move(10, 168)
        self.ip_label_note.setFixedSize(500, 30)

        self.ip = QLineEdit(self)
        self.ip.move(200, 148)
        self.ip.setFixedSize(150, 20)

        self.save_btn = QPushButton('Save', self)
        self.save_btn.move(190, 220)

        self.close_button = QPushButton('Close', self)
        self.close_button.move(275, 220)
        self.close_button.clicked.connect(self.close)

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.statusBar().showMessage('Test Statusbar Message')
    test_list = QStandardItemModel(ex)
    test_list.setHorizontalHeaderLabels(['Name', 'IP', 'Port', 'Time'])
    test_list.appendRow([QStandardItem('1'), QStandardItem('2'), QStandardItem('3')])
    test_list.appendRow([QStandardItem('4'), QStandardItem('5'), QStandardItem('6')])
    ex.connected_clients.setModel(test_list)
    ex.connected_clients.resizeColumnsToContents()
    print('Yo')
    app.exec_()
    print('this is the end')
