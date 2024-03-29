class IncorrectDataRecivedError(Exception):
    """Исключение  - некорректные данные получены от сокета"""
    def __str__(self):
        return 'Принято некорректное сообщение от удалённого компьютера.'


class NonDictInputError(Exception):
    """Исключение - аргумент функции не словарь"""
    def __str__(self):
        return 'Аргумент функции должен быть словарём.'


class ServerError(Exception):
    """
    Класс - исключение, для обработки ошибок сервера.
    При генерации требует строку с описанием ошибки,
    полученную с сервера.
    """
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


class ReqFieldMissingError(Exception):
    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f'В принятом словаре отсутствует ' \
               f'обязательное поле {self.missing_field}.'
