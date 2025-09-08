import logging
import os
import threading

from watchdog.events import FileSystemEventHandler

from logger.constants import PROJECTS
from logger.logging_config import setup_logging

setup_logging()


class LogFileHandler(FileSystemEventHandler):
    DEBOUNCE_SECONDS = 0.5

    def __init__(self, bot, projects: dict[str, dict] = PROJECTS):
        self.bot = bot
        self.projects = projects
        self.log_dir_to_project = {
            config['log_path']: name for name, config in projects.items()
        }
        self.last_run_id = {}
        self.debounce_timers = {}

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith('.log'):
            return

        project_name = self._get_project_from_path(event.src_path)
        if not project_name:
            return

        if project_name in self.debounce_timers:
            self.debounce_timers[project_name].cancel()

        timer = threading.Timer(
            self.DEBOUNCE_SECONDS,
            self.process_log,
            args=(event.src_path, project_name)
        )
        self.debounce_timers[project_name] = timer
        timer.start()

    def process_log(self, file_path, project_name):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                last_lines = f.readlines()[-30:]
        except FileNotFoundError:
            return
        run_id = None

        for line in last_lines:
            if 'RUN_ID=' in line:
                run_id = line.split('RUN_ID=')[1].split(',')[0].strip()
                break

        if not run_id:
            logging.warning(f'В логе {file_path} нет RUN_ID')
            return

        if self.last_run_id.get(project_name) == run_id:
            logging.info(f'RUN_ID={run_id} для {project_name} уже обработан')
            return

        self.last_run_id[project_name] = run_id
        logging.info(f'Готов новый отчёт: {project_name}, RUN_ID={run_id}')
        self.bot.send_project_report(project_name)

    def _get_project_from_path(self, file_path: str):
        file_dir = os.path.dirname(file_path)
        return self.log_dir_to_project.get(file_dir)
