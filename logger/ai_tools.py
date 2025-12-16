import os

from langchain_core.tools import tool

from logger.constants_ai import LOG_PATHS


@tool
def find_and_read_log(
    project: str,
    date_str: str,
    time_str: str = ''
):
    """
    Инструмент для ии-агента, который принимает
    на вход название проекта,
    дату (для поиска директории с логами) и, опционально, время.
    Данная функция находит по переданным аргументам нужный лог-файл
    и читает его
    :param project: Название проекта
    :type project: str
    :param date_str: Дата в формате ГГГГ-ММ-ДД
    :type date_str: str
    :param time_str: Время в формате 10:30 -> 1030
    :type time_str: str
    """
    log_dir = LOG_PATHS.get(project)

    if not log_dir:
        return (
            f'Ошибка: проект {project} не найден. '
            f'Доступные: {list(LOG_PATHS.keys())}'
        )

    if not os.path.exists(log_dir):
        return f'Ошибка: директория {log_dir} не существует'

    date_path = os.path.join(log_dir, date_str)

    if not os.path.exists(date_path):
        return f'Ошибка: нет логов за {date_str}'

    if time_str:
        file_name = date_str.replace('-', '') + time_str + '.log'
        file_path = os.path.join(date_path, file_name)

        if not os.path.exists(file_path):
            return f'Ошибка: файл {file_name} не найден в {date_str}'
    else:
        log_files = [
            file for file in os.listdir(date_path)
            if file.endswith('.log') and len(file) == 16
        ]

        if not log_files:
            return f'Ошибка: нет лог-файлов в {date_str}'

        log_files.sort()
        last_file = log_files[-1]
        file_path = os.path.join(date_path, last_file)

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            return file.read()
    except Exception as error:
        return f'Ошибка чтения файла: {str(error)}'
