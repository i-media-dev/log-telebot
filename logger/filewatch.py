import logging
import os
from collections import deque
from datetime import datetime as dt

from watchdog.events import PatternMatchingEventHandler

from logger.constants import DATE_FORMAT, MAX_PROCESSED_IDS, PROJECTS


class WatchLog(PatternMatchingEventHandler):
    """
    Класс для отслеживания
    появления новых лог-файлов.
    """

    def __init__(self, bot, projects: dict[str, dict] = PROJECTS):
        super().__init__(
            patterns=['*.log'],
            ignore_patterns=['*cron*.log'],
            ignore_directories=True,
            case_sensitive=False
        )

        self.bot = bot
        self.projects = projects
        self.sending_reports: dict = {}
        self.processed_run_ids: deque = deque(maxlen=MAX_PROCESSED_IDS)
        self.log_dir_to_project = {}
        for name, config in projects.items():
            self.log_dir_to_project[config['log_path']] = name

    def on_created(self, event):
        """Метод обрабатывает создание новых лог-файлов."""
        if event.is_directory:
            return

        project_name = self._get_project_from_path(event.src_path)
        if not project_name or not self._is_today_file(event.src_path):
            return

        self._process_log(event.src_path, project_name)

    def _is_today_file(self, file_path: str) -> bool:
        """Метод проверяет, что файл в сегодняшней папке."""
        today_str = dt.now().strftime(DATE_FORMAT)
        return today_str in file_path

    def _get_project_from_path(self, file_path: str):
        """Метод определяет проект по пути к файлу."""
        for log_dir, project_name in self.log_dir_to_project.items():
            if log_dir in file_path:
                return project_name
        return None

    def _process_log(self, file_path: str, project_name: str):
        """Метод обрабатывает лог-файл."""
        today_str = dt.now().strftime(DATE_FORMAT)
        if not os.path.exists(file_path):
            return

        filename = os.path.basename(file_path)
        run_id = filename.replace('.log', '')
        run_key = f'{project_name}_{run_id}'

        if run_key in self.processed_run_ids:
            logging.info(
                'RUN_ID=%s для %s уже обработан',
                run_id,
                project_name
            )
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logging.error('Ошибка чтения файла %s: %s', file_path, e)
            return

        from logger.log_parser import LogParser
        result = LogParser.parse_log_content(content, filename)

        if not result.is_completed:
            logging.info('Файл %s ещё пишется', file_path)
            return

        self.processed_run_ids.append(run_key)
        logging.info(
            'Готов новый отчёт: %s (RUN_ID: %s)',
            project_name,
            run_id
        )
        # self.bot.send_project_report(project_name)

        if self.sending_reports.get(project_name) != today_str:
            self.bot.send_project_report(project_name)
            self.sending_reports[project_name] = today_str
