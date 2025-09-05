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
        logging.info(f'Закрытие файла: {event.src_path}')
        if not event.is_directory:
            current_time = time.time()
            file_path = event.src_path

            if file_path in self.last_processed:
                time_since_last = current_time - self.last_processed[file_path]
                if time_since_last < 60:
                    return

            project_name = self._get_project_from_event(event)
            if project_name:
                logging.info(
                    'Отправка отчета о проекте: '
                    f'{project_name} из файла: {file_path}'
                )
                self.last_processed[file_path] = current_time
                self.bot.send_project_report(project_name)

    def _get_project_from_event(self, event):
        file_dir = os.path.dirname(event.src_path)

        for log_dir, project_name in self.log_dir_to_project.items():
            if file_dir == log_dir:
                return project_name
        return None
