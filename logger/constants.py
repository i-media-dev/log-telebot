import os

from dotenv import load_dotenv

load_dotenv()

HI_ROBOT = 'hi-robot.png'
LIKE_ROBOT = 'like-robot.png'
DISSLIKE_ROBOT = 'disslike-robot.png'
DEPLOY_ROBOT = 'deploy-robot.png'

SUCCESS_ROBOTS = [
    'chill-robot.png',
    'normalno-robot.png',
    'tralala-robot.png',
    'gatsby-robot.png',
    'statem-robot.png'
    'like-robot.png'
]
"""Мемные роботы для удачных операций."""

ERROR_ROBOTS = [
    'dontpanic-robot.png',
    'okak-robot.png',
    'cry-robot.png',
    'disslike-robot.png'
]
"""Мемные роботы для неудачных операций."""

PROJECTS = {
    'auchan_feed_handler': {
        'log_path': os.getenv('LOG_PATH_AUCHAN', ''),
        'check_time': '07:30',
    },
    'citilink_feed_handler': {
        'log_path': os.getenv('LOG_PATH_CITILINK', ''),
        'check_time': '07:30',
    },
    'eapteka_feed_handler': {
        'log_path': os.getenv('LOG_PATH_EAPTEKA', ''),
        'check_time': '08:00',
    },
    'wb_parser': {
        'log_path': os.getenv('LOG_PATH_WB', ''),
        'check_time': '00:30',
    }
}
"""Константа, содержащая настройки существующих проектов."""

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
