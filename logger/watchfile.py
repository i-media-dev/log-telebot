import logging
import os
import time

from watchdog.events import FileSystemEventHandler

from logger.constants import PROJECTS
from logger.logging_config import setup_logging

setup_logging()


class LogFileHandler(FileSystemEventHandler):

    def __init__(self, bot, projects: dict[str, dict] = PROJECTS):
        self.bot = bot
        self.projects = projects
        self.log_dir_to_project = {}
        self.last_processed = {}
        for project_name, config in projects.items():
            log_dir = config['log_path']
            self.log_dir_to_project[log_dir] = project_name

    def on_closed(self, event):

        if event.is_directory:
            return
        file_path = event.src_path

        if not file_path.endswith('.log'):
            return
        project_name = self._get_project_from_path(file_path)
        if project_name:
            logging.info(f'Обнаружено изменение: {file_path}')
            self.bot.send_project_report(project_name)

    def _get_project_from_path(self, file_path):
        file_dir = os.path.dirname(file_path)
        return self.log_dir_to_project.get(file_dir)
