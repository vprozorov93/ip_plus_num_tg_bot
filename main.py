import csv
import os
import telebot
import config as cfg
import database_ip as db
import proccessing_ip as p_ip

bot = telebot.TeleBot(cfg.token)

    
@bot.message_handler(commands=['start'])
def welcome_message(message):
    """
    Функция выполняется при получении ботом команды /start от пользователя. Отправляет приветственное сообщение.
    Запрашивает у пользователя список IP адресов.

    :param message: Базовый параметр передаваемый в функции API, для определения ботом chat_id и других параметров для
    взаимодействия с пользователем.

    :return: None
    """
    db.data[message.from_user.id] = {'status': 0, 'syllable': None, 'ip_list': None}
    text = "Привет {0.first_name}!\n" \
           "Я - {1.first_name}, призван облегчить тебе жизнь с расчетом новых IP адресов при добавлении нужного числа" \
           " к последнему октету твоего ip адреса, жду от тебя список IP текстом или в CSV файле.\n\n" \
           "Вызови /help, что бы узнать в каком виде мне можно давать список IP на обработку и какие есть ограничения."
    bot.send_message(message.chat.id, text.format(message.from_user, bot.get_me()), parse_mode='html')

@bot.message_handler(commands=['github'])
def github_message(message):
    text = 'Я на (https://github.com/vprozorov93/ip_plus_num_tg_bot-Portfolio-Project- "GitHub")'
    bot.send_message(message.chat.id, text, parse_mode='markdown')
    
    
@bot.message_handler(commands=['help'])
def help_message(message):
    """
    Функция выполняется при получении ботом команды /help от пользователя. Отправляет сообщение с описанием возможностей
    и ограничениях бота.

    :param message: Базовый параметр передаваемый в функции API, для определения ботом chat_id и других параметров для
    взаимодействия с пользователем.

    :return: None
    """
    text = 'Я могу принять:\n' \
           '    - Список IP адресов присланных текстом;\n' \
           '    - CSV файл с IP адресами записанные в одну колонку.\n' \
           'Адреса могут иметь вид 192.168.1.1 или 192.168.1.1/24, а также оба вида в одном списке.\n\n' \
           'В тексте IP адреса могут быть разделены:\n' \
           '    - переносом строки\n' \
           '    - пробелом\n' \
           '    - запятой\n' \
           '    - точкой с запятой\n' \
           '    - нижним подчеркиванием\n\n' \
           'В CSV файле следует расположить IP адреса в в первом столбце без каких-либо знаков\n\n' \
           'Если что-то пойдет не так при обработке списка, я сформирую лог обработки списка и отправлю его тебе ' \
           'для изучения\n\n' \
           'ATTENTION! Я пока не умею определять будут ли соответствовать IP адреса после обработки диапазону IP ' \
           'из сети изначального адреса, так что будь бдителен давая мне например адрес 192.168.1.254/24, ' \
           'получая на выходе 192.168.2.1/24, новый IP адрес будет из другой /24 сети. Если его прописать на железку '\
           'скорее всего ты потеряешь к ней доступ.'
    bot.send_message(message.chat.id, text)


# def show_button(message):
#     markup = telebot.types.InlineKeyboardMarkup()
#     markup.add(telebot.types.InlineKeyboardButton(text='Текст', callback_data="/list"))
#     markup.add(telebot.types.InlineKeyboardButton(text='CSV', callback_data="/csv"))
#     bot.send_message(message.chat.id, text="Что обрабатываем?", reply_markup=markup)
#
#
# @bot.callback_query_handler(func=lambda call: True)
# def query_handler(call):
#     bot.answer_callback_query(callback_query_id=call.id)
#     if call.data == '/list':
#         # processing_ip_list(call)
#         bot.send_message(call.message.chat.id, 'Пришли список IP адресов')
#     elif call.data == '/csv':
#         # processing_csv(call)
#         bot.send_message(call.message.chat.id, 'Пришли CSV с IP адресами')
#
#     # bot.send_message(call.message.chat.id, answer)
#     bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)


@bot.message_handler(content_types=['text'])
def processing_text(message):
    """
    Функция выполняется при получении ботом текстовых сообщений от пользователя. Отправляет запросы пользователю на
    получение от него списка IP адресов и получения значения которое необходимо добавить к последнему октету каждого IP
    адреса в списке полученном от пользователя в зависимости от status пользователя указанного в database_ip.data.
    После получения необходимых вводных обрабатывает список и возвращает пользователю новый список текстом.

    :param message: Базовый параметр передаваемый в функции API, для определения ботом chat_id и других параметров для
    взаимодействия с пользователем.

    :return: None
    """
    if db.data.get(message.from_user.id, None) is None:
        db.data[message.from_user.id] = {'status': 0, 'syllable': None, 'ip_list': None}

    if db.data[message.from_user.id]['status'] == 0:
        db.data[message.from_user.id]['ip_list'] = message.text
        db.data[message.from_user.id]['status'] = 1
        text = 'Теперь присылай сколько нужно добавить к последнему октету.'
        bot.send_message(message.chat.id, text)
        return None

    if db.data[message.from_user.id]['status'] == 1:
        if not message.text.isdigit():
            text = f'"{message.text}" не является цифрой или числом, пришли цифру или число.'
            bot.send_message(message.chat.id, text)
            return None

        db.data[message.from_user.id]['syllable'] = int(message.text)
        file_name = f'log_{message.from_user.id}.txt'
        result = p_ip.processing_ip_plus_syllable(
            db.data[message.from_user.id]['ip_list'],
            db.data[message.from_user.id]['syllable'],
            file_name
        )

        if result[1] != 0:
            if result[0] == '':
                text = 'Не удалось обработать ваш список. Ошибки по списку можно посмотреть в log файле.\n\n' \
                       'Жду новый список адресов.'
            else:
                text = 'При обработке списка возникли ошибки, их можно посмотреть в log файле.\n\nЖду новый список)'
                bot.send_message(message.chat.id, result[0])

            path_log = os.path.join(os.getcwd(), file_name)
            with open(path_log, 'rb') as log_file:
                file = log_file.read()
                bot.send_document(message.chat.id, ('log.txt', file))
            os.remove(path_log)
        else:
            if result[0] is None:
                text = 'Не найден доступный разделитель в списке IP адресов, воспользуйтесь командой /help'
            else:
                text = 'Жду новый список ;)'
                bot.send_message(message.chat.id, result[0])

        bot.send_message(message.chat.id, text)
        db.data[message.from_user.id]['status'] = 0
        db.data[message.from_user.id]['ip_list'] = None
        db.data[message.from_user.id]['syllable'] = None
        return None


@bot.message_handler(content_types=['document'])
def processing_csv(message):
    """
    Функция выполняется при получении ботом CSV файла от пользователя. Отправляет запросы пользователю на
    получение от него значения которое необходимо добавить к последнему октету каждого IP
    адреса в CSV файле. Обрабатывает CSV файл в строку и помещает ее в database_ip.data для пользователя.

    :param message: Базовый параметр передаваемый в функции API, для определения ботом chat_id и других параметров для
    взаимодействия с пользователем.

    :return: None
    """
    if db.data.get(message.from_user.id, None) is None:
        db.data[message.from_user.id] = {'status': 0, 'syllable': None, 'ip_list': None}

    if db.data[message.from_user.id]['status'] == 0:
        if message.document.file_name[-4:] != '.csv':
            text = 'Работаю только с файлами формата CSV'
            bot.send_message(message.chat.id, text)
            return

        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        path = os.path.join(os.getcwd(), f'list_{message.from_user.id}.csv')

        with open(path, 'wb') as ip_list_file:
            ip_list_file.write(downloaded_file)

        user_ip_list = ''
        with open(path, 'rt', encoding='utf-8-sig') as ip_list_file:
            csv_reader = csv.reader(ip_list_file)
            for ip in csv_reader:
                user_ip_list = f'{user_ip_list}{ip[0]},'

        user_ip_list = user_ip_list.rstrip(',')
        db.data[message.from_user.id]['ip_list'] = user_ip_list
        text = 'Теперь присылай сколько нужно добавить к последнему октету.'
        bot.send_message(message.chat.id, text)
        os.remove(path)
        db.data[message.from_user.id]['status'] = 1
    else:
        text = 'То сколько нужно добавить нужно отправить текстом, жду.'
        bot.send_message(message.chat.id, text)


if __name__ == '__main__':
    bot.polling(none_stop=True)
