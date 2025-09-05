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

    def on_modified(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        current_time = time.time()

        if current_time - self.last_processed.get(file_path, 0) < 2:
            return

        self.last_processed[file_path] = current_time

        if self._check_endlogging(file_path):
            project_name = self._get_project_from_path(file_path)
            if project_name:
                self.bot.send_project_report(project_name)

    def _check_endlogging(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return 'ENDLOGGING=1' in content
        except Exception as e:
            logging.error(f'Произошла ошибка {e}')

    def _get_project_from_path(self, file_path):
        file_dir = os.path.dirname(file_path)
        return self.log_dir_to_project.get(file_dir)
