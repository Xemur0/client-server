from PyQt5 import QtCore, QtWidgets


class UiMainClientWindow(object):
    def setup_ui(self, main_client_window):
        main_client_window.setObjectName("MainClientWindow")
        main_client_window.resize(756, 534)
        main_client_window.setMinimumSize(QtCore.QSize(756, 534))
        self.centralwidget = QtWidgets.QWidget(main_client_window)
        self.centralwidget.setObjectName("centralwidget")
        self.label_contacts = QtWidgets.QLabel(self.centralwidget)
        self.label_contacts.setGeometry(QtCore.QRect(10, 0, 101, 16))
        self.label_contacts.setObjectName("label_contacts")
        self.btn_add_contact = QtWidgets.QPushButton(self.centralwidget)
        self.btn_add_contact.setGeometry(QtCore.QRect(10, 450, 121, 31))
        self.btn_add_contact.setObjectName("btn_add_contact")
        self.btn_remove_contact = QtWidgets.QPushButton(self.centralwidget)
        self.btn_remove_contact.setGeometry(QtCore.QRect(140, 450, 121, 31))
        self.btn_remove_contact.setObjectName("btn_remove_contact")
        self.label_history = QtWidgets.QLabel(self.centralwidget)
        self.label_history.setGeometry(QtCore.QRect(300, 0, 391, 21))
        self.label_history.setObjectName("label_history")
        self.text_message = QtWidgets.QTextEdit(self.centralwidget)
        self.text_message.setGeometry(QtCore.QRect(300, 360, 441, 71))
        self.text_message.setObjectName("text_message")
        self.label_new_message = QtWidgets.QLabel(self.centralwidget)
        self.label_new_message.setGeometry(QtCore.QRect(300, 330, 450, 16))
        self.label_new_message.setObjectName("label_new_message")
        self.list_contacts = QtWidgets.QListView(self.centralwidget)
        self.list_contacts.setGeometry(QtCore.QRect(10, 20, 251, 411))
        self.list_contacts.setObjectName("list_contacts")
        self.list_messages = QtWidgets.QListView(self.centralwidget)
        self.list_messages.setGeometry(QtCore.QRect(300, 20, 441, 301))
        self.list_messages.setObjectName("list_messages")
        self.btn_send = QtWidgets.QPushButton(self.centralwidget)
        self.btn_send.setGeometry(QtCore.QRect(610, 450, 131, 31))
        self.btn_send.setObjectName("btn_send")
        self.btn_clear = QtWidgets.QPushButton(self.centralwidget)
        self.btn_clear.setGeometry(QtCore.QRect(460, 450, 131, 31))
        self.btn_clear.setObjectName("btn_clear")
        main_client_window.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(main_client_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 756, 21))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.menu_2 = QtWidgets.QMenu(self.menubar)
        self.menu_2.setObjectName("menu_2")
        main_client_window.setMenuBar(self.menubar)
        self.statusBar = QtWidgets.QStatusBar(main_client_window)
        self.statusBar.setObjectName("statusBar")
        main_client_window.setStatusBar(self.statusBar)
        self.menu_exit = QtWidgets.QAction(main_client_window)
        self.menu_exit.setObjectName("menu_exit")
        self.menu_add_contact = QtWidgets.QAction(main_client_window)
        self.menu_add_contact.setObjectName("menu_add_contact")
        self.menu_del_contact = QtWidgets.QAction(main_client_window)
        self.menu_del_contact.setObjectName("menu_del_contact")
        self.menu.addAction(self.menu_exit)
        self.menu_2.addAction(self.menu_add_contact)
        self.menu_2.addAction(self.menu_del_contact)
        self.menu_2.addSeparator()
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())
        self.retranslate_ui(main_client_window)
        self.btn_clear.clicked.connect(self.text_message.clear)
        QtCore.QMetaObject.connectSlotsByName(main_client_window)

    def retranslate_ui(self, main_client_window):
        _translate = QtCore.QCoreApplication.translate
        main_client_window.setWindowTitle(_translate("MainClientWindow",
                                                     "Чат Программа alpha "
                                                     "release"))
        self.label_contacts.setText(_translate("MainClientWindow",
                                               "Список контактов:"))
        self.btn_add_contact.setText(_translate("MainClientWindow",
                                                "Добавить контакт"))
        self.btn_remove_contact.setText(_translate("MainClientWindow",
                                                   "Удалить контакт"))
        self.label_history.setText(_translate("MainClientWindow",
                                              "История сообщений:"))
        self.label_new_message.setText(_translate("MainClientWindow",
                                                  "Введите новое сообщение:"))
        self.btn_send.setText(_translate("MainClientWindow",
                                         "Отправить сообщение"))
        self.btn_clear.setText(_translate("MainClientWindow",
                                          "Очистить поле"))
        self.menu.setTitle(_translate("MainClientWindow", "Файл"))
        self.menu_2.setTitle(_translate("MainClientWindow", "Контакты"))
        self.menu_exit.setText(_translate("MainClientWindow", "Выход"))
        self.menu_add_contact.setText(_translate("MainClientWindow",
                                                 "Добавить контакт"))
        self.menu_del_contact.setText(_translate("MainClientWindow",
                                                 "Удалить контакт"))
