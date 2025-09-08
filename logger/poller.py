import logging
import os
import time

from logger.constants import INTERVAL_POLLING, PROJECTS


class Poller:

    def __init__(
        self,
        bot,
        projects=PROJECTS,
        interval=INTERVAL_POLLING
    ):
        self.bot = bot
        self.projects = projects
        self.interval = interval
        self.last_run_ids = {}

    def start(self):
        while True:
            for project_name, config in self.projects.items():
                log_dir = config['log_path']
                if not os.path.exists(log_dir):
                    continue

                today = time.strftime('%Y-%m-%d')
                for filename in os.listdir(log_dir):
                    if today not in filename or not filename.endswith('.log'):
                        continue

                    path = os.path.join(log_dir, filename)
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        if 'ENDLOGGING=1' not in content:
                            continue

                        parts = content.strip().split('RUN_ID=')
                        if len(parts) < 2:
                            continue
                        run_id = parts[-1].split(',')[0].strip()

                        if self.last_run_ids.get(project_name) == run_id:
                            continue

                        self.last_run_ids[project_name] = run_id

                        self.bot.send_project_report(project_name)
                        logging.info(
                            f'{project_name}: обработан RUN_ID={run_id}')

                    except Exception as e:
                        logging.error(f'Ошибка при чтении {path}: {e}')

            time.sleep(self.interval)
