import logging
import os
from datetime import datetime as dt

from logger.constants import OLD_PATHS
from logger.logging_config import setup_logging

setup_logging()


class FileChecker:

    def __init__(self, file_paths: list = OLD_PATHS):
        self.file_paths = file_paths

    def _get_files_info(self, local_path: str):
        file_count = 0
        file_info = []
        try:
            if not os.path.exists(local_path):
                logging.error('Папка %s не существует', local_path)
                return 0, []

            for item in os.listdir(local_path):
                item_path = os.path.join(local_path, item)

                if os.path.isdir(item_path):
                    continue

                try:
                    stat = os.stat(item_path)
                    file_date = dt.fromtimestamp(stat.st_mtime)
                    size_mb = stat.st_size / (1024 * 1024)

                    file_info.append({'date': file_date, 'size': size_mb})
                    file_count += 1

                except Exception as error:
                    logging.error(
                        'Ошибка при обработке файла %s: %s',
                        item,
                        error
                    )
                    continue
        except Exception as error:
            logging.error(
                'Ошибка при сканировании папки %s: %s',
                local_path,
                error
            )
        return file_count, file_info

    def check_files(self) -> list:
        messages = []
        date_today = dt.now().replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )
        for path in self.file_paths:
            date_success_files = 0
            size_files = []
            files_count, files_info = self._get_files_info(path)
            for info in files_info:
                if info['date'].date() == date_today.date():
                    date_success_files += 1
                size_files.append(info['size'])
            if size_files:
                avg_size = round(
                    sum(size_files) / len(size_files),
                    2
                )
            else:
                avg_size = 0
            message = (
                f'На сервере обновлено {date_success_files}/{files_count} '
                f'файлов проекта {path}. Средний размер файлов {avg_size} мб.'
            )
            messages.append(message)
        return messages
