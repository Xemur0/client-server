Common Package
==============

Пакет общих утилит, использующихся в разных модулях проекта.

Script decorators.py
--------------------

.. automodule:: common.decorators
   :members:

Script descriptors.py
---------------------

.. automodule:: common.descriptors
   :members:

Script errors.py
-------------------

.. autoclass:: common.errors.ServerError
   :members:

Script metaclasses.py
----------------------

.. autoclass:: common.metaclasses.ServerVerifier
   :members:

.. autoclass:: common.metaclasses.ClientVerifier
   :members:

Script utils.py
---------------------

common.utils. **get_message** (client)


   Функция приёма сообщений от удалённых компьютеров. Принимает сообщения JSON,
	декодирует полученное сообщение и проверяет что получен словарь.

common.utils. **send_message** (sock, message)


	Функция отправки словарей через сокет. Кодирует словарь в формат JSON и отправляет через сокет.


Script variables.py
---------------------

Содержит разные глобальные переменные проекта.