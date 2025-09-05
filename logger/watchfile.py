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
        if not getattr(event, "is_write", True):
            return
        file_path = event.src_path
        current_time = time.time()
        if file_path in self.last_processed:
            if current_time - self.last_processed[file_path] < 2:
                return
        self.last_processed[file_path] = current_time
        project_name = self._get_project_from_event(event)
        if project_name:
            logging.info(
                f'Отправка отчета о проекте: {project_name} '
                f'из файла: {file_path}'
            )
            self.bot.send_project_report(project_name)

    def _get_project_from_event(self, event):
        file_dir = os.path.dirname(event.src_path)
        return self.log_dir_to_project.get(file_dir)
