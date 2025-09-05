import logging
import os
from datetime import datetime as dt

from dotenv import load_dotenv

from logger.constants import PROJECTS
from logger.logging_config import setup_logging

load_dotenv()
setup_logging()


class LogMonitor:

    def __init__(self, projects: dict[str, str] = PROJECTS):
        self.projects = projects

    def check_logs(self, project_name: str, last_run_ids: dict) -> tuple[str, str, str]:
        """Проверка логов проекта."""
        today = dt.now().strftime('%Y-%m-%d')
        project = self.projects[project_name]
        log_path = project['log_path']
        if not os.path.exists(log_path):
            message = f'❌ Файл лога не найден: {log_path}'
            return 'NOTFOUND', message, None
        try:
            for filename in os.listdir(log_path):
                if today in filename:
                    file_path = os.path.join(log_path, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        log_content = f.read()
                        time_match = 'EXECUTION_TIME=' in log_content \
                            and log_content.split(
                                'EXECUTION_TIME='
                            )[1].split(' сек')[0]
                        exec_time = time_match if time_match else 'неизвестно'
                        date_match = 'DATE=' in log_content \
                            and log_content.split('DATE=')[1].split(',')[0]
                        date = date_match if date_match else today

                        if 'ENDLOGGING=1' not in log_content:
                            message = 'Файл еще пишется'
                            return 'PENDING', message, None
                        run_id = None

                        if 'RUN_ID' in log_content:
                            run_id = log_content.split('RUN_ID=')[1].split()[0]

                        if run_id and last_run_ids.get(project_name) == run_id:
                            message = 'Отчёт уже отправлен'
                            return 'DUPLICATE', message, run_id

                        if 'SCRIPT_FINISHED_STATUS=SUCCESS' in log_content:
                            message = (
                                f'✅ Скрипт {project_name} выполнен успешно\n'
                                f'📅 Дата: {date}\n'
                                f'⏱️ Время выполнения: {exec_time} сек. '
                                f'или {round(float(exec_time) / 60, 2)} мин.'
                            )
                            return 'SUCCESS', message, run_id

                        elif 'SCRIPT_FINISHED_STATUS=ERROR' in log_content:
                            error_type_match = 'ERROR_TYPE=' in log_content \
                                and log_content.split(
                                    'ERROR_TYPE='
                                )[1].split(',')[0]
                            error_type = error_type_match \
                                if error_type_match else 'неизвестно'
                            error_message_match = 'ERROR_MESSAGE=' \
                                in log_content and log_content.split(
                                    'ERROR_MESSAGE='
                                )[1].split(',')[0]
                            error_message = error_message_match \
                                if error_message_match else 'неизвестно'
                            func_name_match = 'FUNCTION_NAME=' in log_content \
                                and log_content.split(
                                    'FUNCTION_NAME='
                                )[1].split(',')[0]
                            func_name = func_name_match \
                                if func_name_match else 'неизвестно'
                            message = (
                                f'❌ Скрипт {project_name} завершился '
                                'с ошибкой\n'
                                f'📅 Дата: {date}\n'
                                f'⏱️ Время выполнения: {exec_time} сек. '
                                f'или {round(float(exec_time) / 60, 2)} мин.\n'
                                f'💀 Тип ошибки: {error_type}\n'
                                f'🚬 {error_message}\n'
                                f'Функция, бросившая ошибку: {func_name}'
                            )
                            return 'ERROR', message, run_id
                        else:
                            message = 'Статус выполнения не определен'
                            return 'WARNING', message, None
            message = f'Сегодняшний лог для {project_name} не найден'
            return 'ERROR', message, None
        except Exception as e:
            logging.error(f'Ошибка чтения лога: {e}')
            message = f'❌ Ошибка чтения лога: {str(e)}.'
            return 'ERROR', message, None
