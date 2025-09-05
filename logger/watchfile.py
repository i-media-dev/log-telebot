import os

from watchdog.events import FileSystemEventHandler

from logger.constants import PROJECTS


class LogFileHandler(FileSystemEventHandler):

    def __init__(self, bot, projects: dict[str, dict] = PROJECTS):
        self.bot = bot
        self.projects = projects
        self.log_dir_to_project = {}
        for project_name, config in projects.items():
            log_dir = config['log_path']
            self.log_dir_to_project[log_dir] = project_name

    def on_closed(self, event):
        if event.is_directory:
            return
        if not getattr(event, "is_write", True):
            return
        project_name = self._get_project_from_event(event)

        if project_name:
            self.bot.send_project_report(project_name)

    def _get_project_from_event(self, event):
        file_dir = os.path.dirname(event.src_path)
        return self.log_dir_to_project.get(file_dir)
