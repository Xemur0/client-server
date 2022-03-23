import dis


class ServerVerifier(type):
    """
    Проверка на соответствие Сервера
    """
    def __init__(self, classname, bases, classdict):

        methods = []

        attrs = []

        for func in classdict:

            try:
                ret = dis.get_instructions(classdict[func])

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
            raise TypeError('Использование метода connect недопустимо '
                            'в серверном классе')

        if not ('SOCK_STREAM' in attrs and 'AF_INET' in attrs):
            raise TypeError('Некорректная инициализация сокета.')
        super().__init__(classname, bases, classdict)


class ClientVerifier(type):
    """
    Проверка на соответствие Клиента
    """
    def __init__(self, classname, bases, classdict):

        methods = []
        for func in classdict:

            try:
                ret = dis.get_instructions(classdict[func])

            except TypeError:
                pass
            else:

                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)

        for command in ('accept', 'listen', 'socket'):
            if command in methods:
                raise TypeError('В классе обнаружено использование '
                                'запрещённого метода')

        if 'get_message' in methods or 'send_message' in methods:
            pass
        else:
            raise TypeError('Отсутствуют вызовы функций, работающих '
                            'с сокетами.')
        super().__init__(classname, bases, classdict)
