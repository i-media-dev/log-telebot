import logging
import os
from datetime import datetime as dt

from watchdog.events import FileSystemEventHandler

from logger.constants import PROJECTS
from logger.logging_config import setup_logging

setup_logging()


class LogFileHandler(FileSystemEventHandler):

    def __init__(self, bot, projects: dict[str, dict] = PROJECTS):
        self.bot = bot
        self.projects = projects
        self.log_dir_to_project = {
            config['log_path']: name for name, config in projects.items()
        }
        self.last_run_id = {}

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith('.log'):
            return

        project_name = self._get_project_from_path(event.src_path)
        if not project_name:
            return

        today_str = dt.now().strftime('%Y-%m-%d')
        filename = os.path.basename(event.src_path)

        if today_str not in filename or 'cron' in filename.lower():
            return

        self.process_log(event.src_path, project_name)

    def process_log(self, file_path, project_name):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            logging.warning(f'Файл не найден: {file_path}')
            return

        run_id = None
        end_logging_found = False

        for line in reversed(lines):
            if 'RUN_ID=' in line and not run_id:
                run_id = line.split('RUN_ID=')[1].split(',')[0].strip()
            if 'ENDLOGGING=1' in line:
                end_logging_found = True
            if run_id and end_logging_found:
                break

        if not run_id:
            logging.warning(f'В логе {file_path} нет RUN_ID')
            return

        if not end_logging_found:
            logging.info(f'Файл {file_path} ещё пишется')
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
