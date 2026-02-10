import os

from dotenv import load_dotenv

load_dotenv()

SEND_MESSAGE_RETRIES = 5
"""Количество попыток для отправки сообщения."""

USERNAME = os.getenv('USERNAME_FTP')
"""Логин FTP юзера."""

HOST = os.getenv('HOST_FTP')
"""Хост FTP сервера."""

PASSWORD = os.getenv('PASSWORD_FTP')
"""Пароль к FTP серверу."""

HI_ROBOT = 'hi-robot.png'
LIKE_ROBOT = 'like-robot.png'
DISSLIKE_ROBOT = 'disslike-robot.png'
DEPLOY_ROBOT = 'deploy-robot.png'
COFFE_ROBOT = 'coffe-robot.png'
COUNT_ROBOT = 'count-robot.png'

GNEWS_URL = 'https://gnews.io/api/v4/top-headlines'
"""Эндпоинт новостного апи."""

TIME_FOR_ALLERT = '10:00'
"""Время для оповещения по количеству отработанных скриптов."""

DATE_FORMAT = '%Y-%m-%d'
"""Формат даты по умолчанию."""

DEPLOY_ROBOTS = [
    'deploy-robot.png',
    'rocket-robot.png'
]
"""Мемные роботы для деплоя."""

SUCCESS_ROBOTS = [
    'chill-robot.png',
    'normalno-robot.png',
    'tralala-robot.png',
    'gatsby-robot.png',
    'statem-robot.png',
    'like-robot.png'
]
"""Мемные роботы для удачных операций."""

ERROR_ROBOTS = [
    'dontpanic-robot.png',
    'okak-robot.png',
    'cry-robot.png',
    'disslike-robot.png',
    'rage-robot.png',
    'yakubovich-robot.png'
]
"""Мемные роботы для неудачных операций."""

OFF_PROJECTS = ('wb_parser', 'file_stealer_bot(carmoney)')
"""Отключенные скрипты или не попадающие в отбивку."""

PROJECTS = {
    'auchan_feed_handler': {
        'log_path': os.getenv('LOG_PATH_AUCHAN', '')
    },
    'citilink_feed_handler': {
        'log_path': os.getenv('LOG_PATH_CITILINK', '')
    },
    'divanchik_feed_handler': {
        'log_path': os.getenv('LOG_PATH_DIVANCHIK', '')
    },
    'eapteka_feed_handler': {
        'log_path': os.getenv('LOG_PATH_EAPTEKA', '')
    },
    'globus_feed_handler': {
        'log_path': os.getenv('LOG_PATH_GLOBUS', '')
    },
    'uvi_feed_handler': {
        'log_path': os.getenv('LOG_PATH_UVI', '')
    },
    'file_stealer_bot(carmoney)': {
        'log_path': os.getenv('LOG_PATH_CARMONEY', '')
    },
    'wb_parser': {
        'log_path': os.getenv('LOG_PATH_WB', '')
    },
    'yvesrocher_feed_handler': {
        'log_path': os.getenv('LOG_PATH_YVESROCHER', '')
    }
}
"""
Константа, содержащая настройки существующих
проектов (в новых версиях только путь до логов).
"""

MAX_PROCESSED_IDS = 500
"""Максимальный размер множества с run_id логов."""

MEMES = [
    'dontpanic-robot.png',
    'normalno-robot.png',
    'okak-robot.png',
    'tralala-robot.png',
    'chill-robot.png',
    'cry-robot.png',
    'gatsby-robot.png',
    'statem-robot.png'
]
"""Мемы."""

NEW_PATHS = [
    '/home/main_ftp_user/projects/auchan/new_feeds',
    '/home/main_ftp_user/projects/citilink/new_feeds',
    '/home/main_ftp_user/projects/divanchik/new_feeds',
    '/home/main_ftp_user/projects/eapteka/new_feeds',
    '/home/main_ftp_user/projects/globus/new_feeds',
    '/home/main_ftp_user/projects/uvi/new_feeds',
    '/home/main_ftp_user/projects/yvesrocher/new_feeds'
]
"""Список путей к обработанным фидам на FTP."""

OLD_PATHS = [
    '/home/egor/project/auchan/temp_feeds',
    '/home/egor/project/citilink/temp_feeds',
    '/home/egor/project/divanchik/temp_feeds',
    '/home/egor/project/eapteka/temp_feeds',
    '/home/egor/project/globus/temp_feeds',
    '/home/egor/project/uvi/temp_feeds',
    '/home/egor/project/yvesrocher/temp_feeds'
]
"""Список путей к скачанным фидам на сервер."""
