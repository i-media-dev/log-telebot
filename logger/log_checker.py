import logging
import os
from datetime import datetime as dt
from typing import Tuple

from logger.constants import DATE_FORMAT, PROJECTS
from logger.log_parser import LogParser, LogParseResult


class LogChecker:
    """Класс для проверки логов проекта."""

    def __init__(self, projects: dict[str, dict[str, str]] = PROJECTS):
        self.projects = projects
        self.unknown_msg = 'неизвестно'

    def _get_latest_log_file(self, log_dir: str) -> str:
        """Возвращает самый свежий лог-файл в директории."""
        try:
            log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
            return os.path.join(
                log_dir,
                sorted(log_files, reverse=True)[0]
            ) if log_files else ''
        except OSError as error:
            logging.error('Ошибка доступа к директории %s: %s', log_dir, error)
            return ''

    def _read_log_file(self, file_path: str) -> str:
        """Читает содержимое лог-файла."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logging.error(f'Ошибка чтения файла {file_path}: {e}')
            return ''

    def _format_message(
        self,
        project_name: str,
        result: LogParseResult
    ) -> Tuple[str, str]:
        """Форматирует сообщение на основе результатов парсинга."""
        base_info = f'📅 Дата: {result.date or self.unknown_msg}\n'

        if result.execution_time > 0:
            exec_info = (
                f'⏱️ Время выполнения: {result.execution_time} сек. '
                f'({round(result.execution_time / 60, 2)} мин.)\n'
            )
        else:
            exec_info = '⏱️ Время выполнения: неизвестно\n'

        info_bot_section = ''
        if result.info_bot_messages:
            info_lines = [f'• {msg}' for msg in result.info_bot_messages]
            info_bot_section = '\n🤖 Детали:\n' + '\n'.join(info_lines)

        if result.status == 'SUCCESS':
            message = (
                f'✅ Скрипт {project_name} выполнен успешно\n'
                f'{base_info}{exec_info}{info_bot_section}'
            )
            return 'SUCCESS', message

        elif result.status == 'ERROR':
            error_details = (
                f'💀 Тип ошибки: {result.error_type or self.unknown_msg}\n'
                f'🚬 Сообщение: {result.error_message or self.unknown_msg}\n'
                f'🔧 Функция: {result.function_name or self.unknown_msg}'
            )
            message = (
                f'❌ Скрипт {project_name} завершился с ошибкой\n'
                f'{base_info}{exec_info}{error_details}{info_bot_section}'
            )
            return 'ERROR', message

        elif result.status == 'PENDING':
            return 'PENDING', 'Файл еще пишется'

        else:
            message = (
                f'⚠️ Статус выполнения не определен\n'
                f'{base_info}{info_bot_section}'
            )
            return 'WARNING', message

    def check_logs(self, project_name: str) -> Tuple[str, str]:
        """Проверяет логи проекта и возвращает статус и сообщение."""
        project = self.projects.get(project_name)
        if not project:
            return 'ERROR', f'Проект {project_name} не найден'

        log_path = project['log_path']
        if not os.path.exists(log_path):
            return 'NOTFOUND', f'❌ Директория логов не найдена: {log_path}'

        today_dir = dt.now().strftime(DATE_FORMAT)
        today_log_path = os.path.join(log_path, today_dir)

        if not os.path.exists(today_log_path):
            return (
                'NOTFOUND',
                f'❌ Сегодняшние логи для {project_name} не найдены'
            )

        latest_log = self._get_latest_log_file(today_log_path)
        if not latest_log:
            return 'NOTFOUND', f'❌ Лог-файлы для {project_name} не найдены'

        content = self._read_log_file(latest_log)
        if content is None:
            return 'ERROR', f'❌ Не удалось прочитать лог: {latest_log}'

        filename = os.path.basename(latest_log)
        result = LogParser.parse_log_content(content, filename)

        return self._format_message(project_name, result)
