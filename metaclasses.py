import dis


# Метакласс для проверки соответствия сервера:
class ServerVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        # clsname - экземпляр метакласса - Server
        # bases - кортеж базовых классов - ()
        # clsdict - словарь атрибутов и методов экземпляра метакласса
        # {'__module__': '__main__',
        # '__qualname__': 'Server',
        # 'port': <descrptrs.Port object at 0x000000DACC8F5748>,
        # '__init__': <function Server.__init__ at 0x000000DACCE3E378>,
        # 'init_socket': <function Server.init_socket at 0x000000DACCE3E400>,
        # 'main_loop': <function Server.main_loop at 0x000000DACCE3E488>,
        # 'process_message': <function Server.process_message at 0x000000DACCE3E510>,
        # 'process_client_message': <function Server.process_client_message at 0x000000DACCE3E598>}

        methods = []

        attrs = []

        for func in clsdict:

            try:
                ret = dis.get_instructions(clsdict[func])

            except TypeError:
                pass
            else:

                for i in ret:
                    print(i)

                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attrs:
                            attrs.append(i.argval)
        print(methods)

        if 'connect' in methods:
            raise TypeError('Использование метода connect недопустимо в серверном классе')

        if not ('SOCK_STREAM' in attrs and 'AF_INET' in attrs):
            raise TypeError('Некорректная инициализация сокета.')
        # Обязательно вызываем конструктор предка:
        super().__init__(clsname, bases, clsdict)


class ClientVerifier(type):
    def __init__(self, clsname, bases, clsdict):

        methods = []
        for func in clsdict:

            try:
                ret = dis.get_instructions(clsdict[func])

            except TypeError:
                pass
            else:

                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)

        for command in ('accept', 'listen', 'socket'):
            if command in methods:
                raise TypeError('В классе обнаружено использование запрещённого метода')

        if 'get_message' in methods or 'send_message' in methods:
            pass
        else:
            raise TypeError('Отсутствуют вызовы функций, работающих с сокетами.')
        super().__init__(clsname, bases, clsdict)
