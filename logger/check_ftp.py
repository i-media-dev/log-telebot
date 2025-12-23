from datetime import datetime as dt
from ftplib import FTP

from logger.constants import NEW_PATHS


class FtpChecker:

    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password

    def _get_files_info(self, path: str):
        files: list = []
        ftp = FTP(self.host)
        ftp.login(self.username, self.password)
        ftp.cwd(path)
        ftp.retrlines('LIST', files.append)
        file_count = 0
        file_info = []
        for line in files:
            parts = line.split()

            if len(parts) < 9:
                continue

            if parts[0].startswith('d'):
                continue
            date_str = ' '.join(parts[5:7])
            date_with_year_str = f'{date_str} {dt.now().year}'
            file_date = dt.strptime(date_with_year_str, '%b %d %Y')
            file_count += 1

            file_info.append({
                'date': file_date,
                'size': int(parts[4])
            })
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
        for path in NEW_PATHS:
            date_success_files = 0
            size_success_files = []
            files_count, files_info = self._get_files_info(path)
            for info in files_info:
                if info['date'].date() == date_today.date():
                    date_success_files += 1
                size_success_files.append(info['size'])
            message = (
                f'На FTP обновлено {date_success_files}/{files_count} '
                f'файлов проекта {path}. '
            )
            messages.append(message)
        return messages
