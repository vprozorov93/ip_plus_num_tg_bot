import os
import re


def _find_separator(string_ip):
    """
    Вспомогательная функция используется в функциях _make_ip_list и _make_log_file для определения разделителя IP
    адресов в пользовательской строке.

    :param string_ip: Строка с IP адресами полученная от пользователя.

    :return: Возвращает значение разделителя в строке string_ip.
    """
    if ',\n' in string_ip:
        separator = ',\n'
    elif '\n' in string_ip:
        separator = '\n'
    elif ',' in string_ip:
        separator = ','
    elif ' ' in string_ip:
        separator = ' '
    elif ';' in string_ip:
        separator = ';'
    else:
        separator = '_'

    return separator


def _make_ip_list(string_ip):
    """
    Вспомогательная функция, вызывается из основной функции processing_ip_plus_syllable для обработки строки с IP
    адресами, полученной от пользователя с целью преобразования ее в список.
    Используется также в функции _make_log_file.

    :param string_ip: Строка с IP адресами полученная от пользователя.

    :return: Возвращает список IP адресов, полученных из строки введенной пользователем.
    """
    separator = _find_separator(string_ip)
    string_ip_list = string_ip.split(separator)

    for i in range(0, len(string_ip_list)):
        string_ip_list[i] = string_ip_list[i].replace(' ', '')

        if "/" not in string_ip_list[i]:
            string_ip_list[i] = [string_ip_list[i], 'no_mask']
        else:
            string_ip_list[i] = string_ip_list[i].split('/')

        valid_ip = re.fullmatch(r'\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}', string_ip_list[i][0])

        if valid_ip is not None:
            string_ip_list[i][0] = string_ip_list[i][0].split('.')
            for j in range(0, len(string_ip_list[i][0])):
                if int(string_ip_list[i][0][j]) > 255:
                    string_ip_list[i][0] = 'invalid_ip_on_input'
                    break
                j += 1
        else:
            string_ip_list[i][0] = 'invalid_ip_on_input'

        if string_ip_list[i][1] != 'no_mask':
            valid_mask = re.fullmatch(r'\d{1,2}', string_ip_list[i][1])
            if valid_mask is not None:
                if int(string_ip_list[i][1]) > 32 or int(string_ip_list[i][1]) < 1:
                    string_ip_list[i][1] = 'invalid_mask_on_input'
            else:
                string_ip_list[i][1] = 'invalid_mask_on_input'
        i += 1

    return string_ip_list


def _make_log_file(string_ip, processed_ip_list, error, file_name='log.txt'):
    """
    Вспомогательная функция, вызывается из основной функции processing_ip_plus_syllable для формирования текста
    и записи файла лога работы основной функции.

    :param string_ip: Строка с IP адресами полученная от пользователя.

    :param processed_ip_list: Результат обработки полученной от пользователя строки
    с IP адресами функцией processing_ip_plus_syllable в виде списка.

    :param error: Количество возникших ошибок при работе функции processing_ip_plus_syllable.

    :param file_name: Имя для создаваемого лог файла.

    :return: Функция ничего не возвращает, а создает log файл в текущей директории.
    """
    with open(os.path.join(os.getcwd(), file_name), 'wt') as file:
        separator = _find_separator(string_ip)
        input_ip_list = string_ip.split(separator)
        new_list_ip = []
        for ip, mask in processed_ip_list:
            if ip == 'invalid_ip_on_input' or ip == 'invalid_ip_when_processing':
                if mask == 'invalid_mask_on_input':
                    new_list_ip.append(f'Error: {ip} and {mask}')
                else:
                    new_list_ip.append(f'Error: {ip}')
            elif mask == 'invalid_mask_on_input':
                new_list_ip.append(f'Error: {mask}. ip_not_processed')
            elif mask == 'no_mask':
                new_list_ip.append(f'Success: {ip}')
            else:
                new_list_ip.append(f'Success: {ip}/{mask}')
        log_string = f'Error: {error}pcs\n\n'
        for index in range(0, len(input_ip_list)):
            log_string += f'{input_ip_list[index]} --->>> {new_list_ip[index]}\n'

        file.write(log_string)
    return None


def processing_ip_plus_syllable(string_ip: str, syllable: int, file_name='_log.txt'):
    """
    Функция обрабатывает полученную на входе строку состоящую из IP адресов добавляя указанное значение к последнему
     октету.

    :param string_ip: Строка состоящая из IP адресов разделенных одним из символов:
        - переносом строки;
        - пробелом;
        - запятой;
        - точкой с запятой;
        - нижним подчеркиванием.

    :param syllable: Число или цифра, которое необходимо прибавить к последнему октету каждого IP адреса из string_ip.

    :param file_name: Название для создания файла лога с расширением txt, по-умолчанию значение _log.txt.
    В случае, если при обработке string_ip возникнут ошибки, функция создаст log файл, который
    содержит результат обработки каждого IP адреса из string_ip и текст ошибки, если она возникла при итерации.

    :return: Возвращает список вида [строка с обработанными ip адресами, количество возникших ошибок].
    """
    list_ip = _make_ip_list(string_ip)
    error = 0
    for ip, mask in list_ip:
        if ip == 'invalid_ip_on_input':
            error += 1
            continue

        ip.reverse()

        for octet in range(len(ip)):
            if octet == 0:
                ip[octet] = int(ip[octet])+syllable
                if int(ip[octet]) > 255:
                    ip[octet] = int(ip[octet])-255
                    ip[octet+1] = int(ip[octet+1])+1
            elif octet == 1 or octet == 2:
                if int(ip[octet]) > 255:
                    ip[octet] = int(ip[octet]) - 255
                    ip[octet+1] = int(ip[octet+1])+1
            elif octet == 3:
                if int(ip[octet]) > 255:
                    list_ip[list_ip.index([ip, mask])][0] = 'invalid_ip_when_processing'
                    ip = 'invalid_ip_when_processing'
                    error += 1
                else:
                    list_ip[list_ip.index([ip, mask])][0].reverse()
            octet += 1

        if ip != 'invalid_ip_when_processing':
            ip_string = ''
            for octet in list_ip[list_ip.index([ip, mask])][0]:
                ip_string += f'{octet}.'
            list_ip[list_ip.index([ip, mask])] = [ip_string.rstrip('.'), mask]

    new_string_ip = ''
    for ip, mask in list_ip:
        if ip == 'invalid_ip_on_input' or ip == 'invalid_ip_when_processing':
            continue
        elif mask == 'invalid_mask_on_input':
            error += 1
            continue
        elif mask == 'no_mask':
            new_string_ip += f'{ip}\n'
        else:
            new_string_ip += f'{ip}/{mask}\n'

    if error != 0:
        _make_log_file(string_ip, list_ip, error, file_name)

    return [new_string_ip, error]
