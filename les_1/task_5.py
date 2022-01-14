"""
Задание 5.

Выполнить пинг веб-ресурсов yandex.ru, youtube.com и
преобразовать результаты из байтовового в строковый тип на кириллице.

Подсказки:
--- используйте модуль chardet, иначе задание не засчитается!!!
"""

import subprocess
import chardet

ARGS_FOR_YANDEX = ['ping', 'yandex.ru']
ARGS_FOR_YOUTUBE = ['ping', 'youtube.com']
ARGS = [ARGS_FOR_YANDEX, ARGS_FOR_YOUTUBE]

for i in ARGS:
    ping = subprocess.Popen(i, stdout=subprocess.PIPE)
    for i in ping.stdout:
        result = chardet.detect(i)
        i = i.decode(result['encoding']).encode('utf-8')
        print(i.decode('utf-8'))
