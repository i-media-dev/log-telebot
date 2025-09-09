# import logging
# import time
# import threading

# from logger.constants import INTERVAL_POLLING


# class LogPoller:
#     def __init__(self, bot, interval=INTERVAL_POLLING):
#         self.bot = bot
#         self.interval = interval
#         self.last_run_ids = {}
#         self.running = True

#     def start(self):
#         thread = threading.Thread(target=self._poll_loop)
#         thread.daemon = True
#         thread.start()
#         logging.info(f'LogPoller запущен с интервалом {self.interval} сек')

#     def stop(self):
#         self.running = False

#     def _poll_loop(self):
#         while self.running:
#             try:
#                 self._check_all_projects()
#             except Exception as e:
#                 logging.error(f'Ошибка в poll loop: {e}')
#             time.sleep(self.interval)

#     def _check_all_projects(self):
#         for project_name in self.bot.log_monitor.projects:
#             self._check_project(project_name)

#     def _check_project(self, project_name):
#         try:
#             tag, result = self.bot.log_monitor.check_logs(project_name)

#             if tag not in ['PENDING', 'WARNING', 'DUPLICATE', 'NOTFOUND']:
#                 run_id = self._extract_run_id_from_result(result)

#                 if run_id and self.last_run_ids.get(project_name) != run_id:
#                     self.last_run_ids[project_name] = run_id
#                     logging.info(
#                         'Найден новый отчет: '
#                         f'{project_name}, RUN_ID={run_id}'
#                     )
#                     self.bot.send_project_report(project_name)
#                 elif run_id:
#                     logging.debug(
#                         f'RUN_ID={run_id} уже обработан для {project_name}')

#         except Exception as e:
#             logging.error(f'Ошибка проверки проекта {project_name}: {e}')

#     def _extract_run_id_from_result(self, result):
#         if 'RUN_ID=' in result:
#             try:
#                 return result.split('RUN_ID=')[1].split()[0]
#             except (IndexError, AttributeError):
#                 return None
#         return None
