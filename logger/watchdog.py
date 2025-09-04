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
        if not event.is_directory:
            project_name = self._get_project_from_event(event)
            if project_name:
                self.bot.send_project_report(project_name)

    def _get_project_from_event(self, event):
        file_path = event.src_path
        for log_dir, project_name in self.log_dir_to_project.items():
            if file_path.startswith(log_dir):
                return project_name
        return None
