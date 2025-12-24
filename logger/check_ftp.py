import logging
from datetime import datetime as dt
from ftplib import FTP

from logger.constants import NEW_PATHS
from logger.logging_config import setup_logging

setup_logging()


class FtpChecker:

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        file_paths: list = NEW_PATHS
    ):
        self.host = host
        self.username = username
        self.password = password
        self.file_paths = file_paths

    def _get_files_info(self, path: str):
        files: list = []
        ftp = FTP(self.host)
        ftp.login(self.username, self.password)
        ftp.cwd(path)
        ftp.retrlines('LIST', files.append)
        file_count = 0
        file_info = []
        for line in files:
            try:
                parts = line.split()

                if len(parts) < 9:
                    continue

                if parts[0].startswith('d'):
                    continue
                date_str = ' '.join(parts[5:7])
                date_with_year_str = f'{date_str} {dt.now().year}'
                file_date = dt.strptime(date_with_year_str, '%b %d %Y')
                file_count += 1
                size_mb = int(parts[4]) / (1024*1024)

                file_info.append({
                    'date': file_date,
                    'size': size_mb
                })
            except Exception as error:
                logging.error('Ошибка при обработке файла %s: %s', line, error)
        ftp.quit()
        return file_count, file_info

    def check_new_files(self) -> list:
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
            try:
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
                    f'На FTP обновлено {date_success_files}/{files_count} '
                    f'файлов проекта {path}. '
                    f'Средний размер файлов {avg_size} мб.'
                )
            except Exception as error:
                logging.error(
                    'Ошибка получения информации по директории %s: %s',
                    path,
                    error
                )
            messages.append(message)
        return messages
