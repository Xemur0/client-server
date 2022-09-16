"""Unit-тесты клиента"""

import sys
import os
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import TIME, RESPONSE, PRESENCE, ACCOUNT_NAME, USER, ERROR, ACTION

from client import Client_Core


class Test_Class(unittest.TestCase, Client_Core):
    '''
    Класс с тестами
    '''

    def test_def_presense(self):
        """Тест коректного запроса"""
        test = Client_Core.create_presence(self)
        test[TIME] = 1.1  # время необходимо приравнять принудительно
        # иначе тест никогда не будет пройден
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_200_ans(self):
        """Тест корректного разбора ответа 200"""
        self.assertEqual(Client_Core.process_ans(self, {RESPONSE: 200}), '200 : OK')

    def test_400_ans(self):
        """Тест корректного разбора 400"""
        self.assertEqual(Client_Core.process_ans(self, {RESPONSE: 400, ERROR: 'Bad Request'}), '400 : Bad Request')

    def test_no_response(self):
        """Тест исключения без поля RESPONSE"""
        self.assertRaises(TypeError, Client_Core.process_ans, {ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
