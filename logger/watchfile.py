import logging
import os
import threading

from watchdog.events import FileSystemEventHandler

from logger.constants import PROJECTS
from logger.logging_config import setup_logging

setup_logging()


class LogFileHandler(FileSystemEventHandler):
    """Обработчик событий файловых изменений для логов с debounce."""

    DEBOUNCE_SECONDS = 1

    def __init__(self, bot, projects: dict[str, dict] = PROJECTS):
        self.bot = bot
        self.projects = projects
        self.log_dir_to_project = {}
        self.last_processed = {}
        self.debounce_timers = {}

        for project_name, config in projects.items():
            log_dir = config['log_path']
            self.log_dir_to_project[log_dir] = project_name

    def on_closed(self, event):
        if event.is_directory or not event.src_path.endswith('.log'):
            return

        file_path = event.src_path
        project_name = self._get_project_from_path(file_path)
        if not project_name:
            return

        try:
            mtime = os.path.getmtime(file_path)
        except FileNotFoundError:
            return
        last_mtime = self.last_processed.get(file_path)

        if last_mtime == mtime:
            return
        self.last_processed[file_path] = mtime

        if file_path in self.debounce_timers:
            self.debounce_timers[file_path].cancel()

        timer = threading.Timer(
            self.DEBOUNCE_SECONDS, self._process_file, args=(file_path, project_name))
        self.debounce_timers[file_path] = timer
        timer.start()

    def _process_file(self, file_path, project_name):
        """Обрабатываем файл после debounce."""
        try:
            tag, _ = self.bot.log_monitor.check_logs(project_name)
            if tag not in ['SUCCESS', 'ERROR']:
                logging.info(f'Файл {file_path} еще пишется, пропускаем')
                return

            logging.info(
                f'Обнаружено изменение и готовность лога: {file_path}')
            self.bot.send_project_report(project_name)
        finally:
            if file_path in self.debounce_timers:
                del self.debounce_timers[file_path]

    def _get_project_from_path(self, file_path):
        file_dir = os.path.dirname(file_path)
        return self.log_dir_to_project.get(file_dir)
