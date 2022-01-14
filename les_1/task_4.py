"""
Задание 4.

Преобразовать слова «разработка», «администрирование», «protocol»,
«standard» из строкового представления в байтовое и выполнить
обратное преобразование (используя методы encode и decode).

Подсказки:
--- используйте списки и циклы, не дублируйте функции


"""

str_list = ['разработка', 'администрирование', 'protocol', 'standard']

for i in str_list:
    word_encode = i.encode('utf-16')
    print(word_encode)
    word_decode = word_encode.decode('utf-16')
    print(word_decode)
    print()
