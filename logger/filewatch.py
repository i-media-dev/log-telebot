import logging
import os
import threading

from datetime import datetime as dt
from watchdog.events import PatternMatchingEventHandler

from logger.constants import PROJECTS


class LogFileHandler(PatternMatchingEventHandler):
    DEBOUNCE_SECONDS = 3.0

    def __init__(self, bot, projects: dict[str, dict] = PROJECTS):
        super().__init__(
            patterns=['*.log'],
            ignore_patterns=['*cron*.log'],
            ignore_directories=True,
            case_sensitive=False
        )

        self.bot = bot
        self.projects = projects
        self.log_dir_to_project = {
            config['log_path']: name for name, config in projects.items()
        }
        self.last_run_id = {}
        self.processing_flags = {}
        self.debounce_timers = {}
        self.lock = threading.RLock()

    def on_modified(self, event):
        project_name = self._get_project_from_path(event.src_path)
        if not project_name:
            return

        filename = os.path.basename(event.src_path)
        today_str = dt.now().strftime('%Y-%m-%d')
        if today_str not in filename:
            return

        with self.lock:
            if self.processing_flags.get(project_name, False):
                return

            if project_name in self.debounce_timers:
                self.debounce_timers[project_name].cancel()

            timer = threading.Timer(
                self.DEBOUNCE_SECONDS,
                self._process_log,
                args=(event.src_path, project_name)
            )
            self.debounce_timers[project_name] = timer
            timer.start()
            self.processing_flags[project_name] = True

    def _process_log(self, file_path, project_name):
        if not os.path.exists(file_path):
            with self.lock:
                self.processing_flags[project_name] = False
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            logging.debug(f'Файл не найден: {file_path}')
            with self.lock:
                self.processing_flags[project_name] = False
            return
        except Exception as e:
            logging.error(f'Ошибка чтения файла {file_path}: {e}')
            with self.lock:
                self.processing_flags[project_name] = False
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
            logging.debug(f'В логе {file_path} нет RUN_ID')
            with self.lock:
                self.processing_flags[project_name] = False
            return

        if not end_logging_found:
            logging.info(f'Файл {file_path} ещё пишется')
            with self.lock:
                self.processing_flags[project_name] = False
            return

        with self.lock:
            if self.last_run_id.get(project_name) == run_id:
                logging.info(
                    f'RUN_ID={run_id} для {project_name} уже обработан')
                self.processing_flags[project_name] = False
                return
            self.last_run_id[project_name] = run_id

        logging.info(f'Готов новый отчёт: {project_name}, RUN_ID={run_id}')
        self.bot.send_project_report(project_name)

        with self.lock:
            self.processing_flags[project_name] = False

    def _get_project_from_path(self, file_path: str):
        file_dir = os.path.dirname(file_path)
        return self.log_dir_to_project.get(file_dir)
