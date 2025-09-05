import os

from dotenv import load_dotenv

load_dotenv()

HI_ROBOT = 'hi-robot.png'
LIKE_ROBOT = 'like-robot.png'
DISSLIKE_ROBOT = 'disslike-robot.png'
DEPLOY_ROBOT = 'deploy-robot.png'


PROJECTS = {
    'auchan_feed_handler': {
        'log_path': os.getenv('LOG_PATH_AUCHAN'),
        'check_time': '07:30',
    },
    'citilink_feed_handler': {
        'log_path': os.getenv('LOG_PATH_CITILINK'),
        'check_time': '07:30',
    },
    'eapteka_feed_handler': {
        'log_path': os.getenv('LOG_PATH_EAPTEKA'),
        'check_time': '08:00',
    },
    'wb_parser': {
        'log_path': os.getenv('LOG_PATH_WB'),
        'check_time': '00:30',
    }
}
"""Константа, содержащая настройки существующих проектов."""

INTERVAL_POLLING = 60
"""Интервал проверки директории логов."""
