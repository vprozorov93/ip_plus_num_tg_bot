# IP plus num bot for Telegram (for portfolio).

### Для чего?
Бот для мессенджера Телеграм, который просит от пользователя ввести один или несколько IP адресов через разделитель и число или цифра, которое необходимо добавить к его последнему октету. Результатом работы которого будет IP адрес или список IP адресов с прибавленным к последнему октету числом или цифрой полученной от пользователя.

### Немного в историю...
Проект начался c пьянки на кухне одного из друзей, где один из последних сказал, есть на работе кейс, хочу в Excel написать список IP адресов и растянуть функцию, результатом которой будет IP адрес, к которому прибавили какое-то число. Пытался написать, что-то не  выходит. Ну, на пьяную голову, я сказал что решу кейс за 15 минут, и правда, решил за 15 минут, но в формуле была ошибка, и еще 30 минут ушел на ее поиск)

Для тех кому нужна формула в Excel:
=ЛЕВСИМВ(RC[-1];НАЙТИ(".";RC[-1];НАЙТИ(".";RC[-1];НАЙТИ(".";RC[-1];1))+НАЙТИ(".";RC[-1];1)+1))&(ПСТР(RC[-1];НАЙТИ(".";RC[-1];НАЙТИ(".";RC[-1];НАЙТИ(".";RC[-1];1))+НАЙТИ(".";RC[-1];1)+1)+1;10)+2)
В R1C1 пишем IP вида x.x.x.x, в R1C2 вставляем формулу, профит) 

В тот момент я уже месяц изучал Python на курсе в Нетологии и решил сделать ПО, которое берет xlsx файл и обрабатывает в нем IP адреса, записывая в тот же файл результат. Получилось сделать примерно за 3-4 часа, к тому моменту я уже знал что такое переменные, типы данных в Python, функции и прошелся по ООП в рамках курса, так что работе с файлами пришлось посвятить половину из потраченого времени. В конечном итоге собрал исполняемый файл и отправил другу, он доволен, я горд собой. Но...

Но мне сразу пришла мысль, что пересылать этот мини скрипт не очень удобно, качать, хранить его на ПК, так что нужно запилить бота, который принимает от пользователя список текстом или файлом и выдает результат. Итогом стал настоящий проект, телеграм бот, который имеет подобие БД для работы с несколькими пользователями, возможность принимать IP адреса текстом или CSV файлом и отправлять log файл, если при обработке полученных данных от юзера были ошибки. Реализация заняла около 4 дней или 10 часов чистого времени. Был полностью переписана логика обработки ip адресов с использованием регулярных выражений, поддержкой вида ip адреса для которого указана маска подсети вида '/x', и создания log файла с описанием обработки каждого ip адреса, в  случае, если при обработке возникали ошибки. Около 3 часов было потрачено на изучение работы с библиотекой pyTelegramBotAPI.

## Используемые библиотеки Python
Для разработки использовал Python версии 3.9.6

В процессе разработки были использованы базовые библиотеки:
* os
* re
* csv

В качестве библиотеки работы с Telegram API использовалась pyTelegramBotAPI(telebot), для запуска бота ее необходимо установить.

## Установка и запуск
1. Создайте локальный репозиторий проекта у себя на ПК
2. Установите Python версии не ниже 3.9.6
3. Установите pyTelegramBotAPI следующей командой:
    * Windows: ```pip install pytelegrambotapi```
    * MacOS: ```pip3 install pytelegrambotapi```
4. В файл ```config.py``` необходимо поместить токен созданного вами бота через ```@BotFather```
5. Откройте консоль в директории локального репозитория и напишите ```python3 main.py```
6. Бэкэнд бота запущен, можно его гонять в хвост и гриву.

## Краткое описание содержимого проекта
### main.py
Основной файл python бота, который необходио запустить для его работы. Содержит следующие команды обработки сообщений полученных от пользователя:
* Обработка команды /start.
* Обработка команды /help.
* Обработка полученных текстовых сообщения и выполнение конечных расчетов.
* Обработка полученного файла(только в .csv формате) и преобразование данных в список ip адресов(string)

### proccessing_ip.py
Написанная с нуля логика обработки списка(string) полученной от пользователя. Содержит вспомогательные функции:
* _find_separator - ищет разделитель между ip адресами;
* _make_ip_list - возвращает список(list) ip адресов из строки введенной пользователем для дальнейшей обработки;
* _make_log_file - создание log файла обработки списка ip адресов в текущей дерриктории;
* processing_ip_plus_syllable - основная функция обрабатывающая полученные ip адреса от пользователя и возвращающая [новый_список_ip: str, количество_ошибок: int].

### config.py
Хранит переменную token, которая содержит токен бота созданного через ```@BotFather```

### database_ip.py
Содержит переменную data(dict), которая хранит:
1. ключ - user_id пользователя телеграм использующего бота;
2. значение - слварь хранящий ключи:
    * status - 0 или 1 в зависисмости от этапа обработки запроса пользователя;
    * ip_list - полученный от пользователя список(stt) ip адресов;
    * syllable - полученное от пользователя число или цифру, которую необходимо прибавить к последнему октету каждого ip адреса в ip_list.
       
По умолчанию status: 0, ip_list: None, syllable: None .