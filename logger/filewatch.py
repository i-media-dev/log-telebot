import logging
import os
from datetime import datetime as dt

from watchdog.events import PatternMatchingEventHandler

from logger.constants import MAX_PROCESSED_IDS, PROJECTS


class LogFileHandler(PatternMatchingEventHandler):
    """Класс для отслеживания изменений в логах."""

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
        self.processed_run_ids = set()
        self.max_processed_ids = MAX_PROCESSED_IDS

    def on_modified(self, event):
        project_name = self._get_project_from_path(event.src_path)

        if not project_name:
            return

        filename = os.path.basename(event.src_path)
        today_str = dt.now().strftime('%Y-%m-%d')
        if today_str not in filename:
            return
        self._process_log(event.src_path, project_name)

    def _process_log(self, file_path, project_name):
        if not os.path.exists(file_path):
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logging.error(f'Ошибка чтения файла {file_path}: {e}')
            return

        if 'ENDLOGGING=1' not in content:
            logging.info(f'Файл {file_path} ещё пишется')
            return

        run_id = None
        if 'RUN_ID=' in content:
            run_id = content.split('RUN_ID=')[1].split(',')[0].strip()

        if run_id:
            run_key = f'{project_name}_{run_id}'
            if run_key in self.processed_run_ids:
                logging.info(
                    f'RUN_ID={run_id} для {project_name} уже обработан')
                return

            if len(self.processed_run_ids) >= self.max_processed_ids:
                self.processed_run_ids.clear()
            self.processed_run_ids.add(run_key)

        logging.info(f'Готов новый отчёт: {project_name}')
        self.bot.send_project_report(project_name)

    def _get_project_from_path(self, file_path: str):
        file_dir = os.path.dirname(file_path)
        return self.log_dir_to_project.get(file_dir)
