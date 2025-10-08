import os

from dotenv import load_dotenv

load_dotenv()

HI_ROBOT = 'hi-robot.png'
LIKE_ROBOT = 'like-robot.png'
DISSLIKE_ROBOT = 'disslike-robot.png'
DEPLOY_ROBOT = 'deploy-robot.png'

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
    'rage-robot.png'
]
"""Мемные роботы для неудачных операций."""

PROJECTS = {
    'auchan_feed_handler': {
        'log_path': os.getenv('LOG_PATH_AUCHAN', '')
    },
    'citilink_feed_handler': {
        'log_path': os.getenv('LOG_PATH_CITILINK', '')
    },
    'eapteka_feed_handler': {
        'log_path': os.getenv('LOG_PATH_EAPTEKA', '')
    },
    'uvi_feed_handler': {
        'log_path': os.getenv('LOG_PATH_UVI', '')
    },
    'wb_parser': {
        'log_path': os.getenv('LOG_PATH_WB', '')
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
