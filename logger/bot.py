import logging
import os
import threading

from telebot import TeleBot, types
from dotenv import load_dotenv

# from watchdog.observers import Observer
from logger.constants import (
    DISSLIKE_ROBOT,
    HI_ROBOT,
    LIKE_ROBOT,
    PROJECTS
)
from logger.log_monitor import LogMonitor
from logger.logging_config import setup_logging
# from logger.filewatch import LogFileHandler
from logger.poller import LogPoller

setup_logging()
load_dotenv()


class IBotLog:
    """Класс управления телеграм-ботом."""

    def __init__(
        self,
        token: str,
        group_id=os.getenv('GROUP_ID'),
        log_monitor=None
    ):
        self.token = token
        self.log_monitor = log_monitor or LogMonitor()
        self.bot = TeleBot(token)
        self.group_id = int(group_id)
        self.active_users = set()
        # self.log_observer = None
        self.lock = threading.RLock()
        self.setup_handlers()
        self.setup_file_watcher()

    def get_robot(self, robot, chat_id):
        try:
            with open(f'robot/{robot}', 'rb') as photo:
                self.bot.send_sticker(chat_id, photo)
        except FileNotFoundError:
            logging.warning(f'Робот {robot} не найден')

    def send_message_str(self, chat_id, message_str, keyboard=None):
        try:
            self.bot.send_message(
                chat_id=chat_id,
                text=message_str,
                reply_markup=keyboard
            )
            logging.info(f'Сообщение отправлено получателю {chat_id}')
        except Exception as e:
            logging.error(f'Ошибка при отправке сообщения: {e}')
            raise

    def setup_file_watcher(self):
        # self.log_observer = Observer()
        # event_handler = LogFileHandler(self)

        # for project_config in PROJECTS.values():
        #     log_dir = project_config['log_path']
        #     self.log_observer.schedule(
        #         event_handler,
        #         log_dir,
        #         recursive=False
        #     )

        # self.log_observer.start()
        self.poller = LogPoller(self)
        self.poller.start()

    def send_project_report(self, project_name: str):
        tag, result = self.log_monitor.check_logs(project_name)
        logging.info(
            f'send_project_report вызван для {project_name}, tag={tag}')

        if tag in ['PENDING', 'WARNING', 'DUPLICATE', 'NOTFOUND']:
            return

        report_id = f'{project_name}_{tag}'

        with self.lock:
            if hasattr(
                self,
                '_processing_reports'
            ) and report_id in self._processing_reports:
                logging.info(
                    f'Отчет {report_id} уже обрабатывается, пропускаем')
                return

            if not hasattr(self, '_processing_reports'):
                self._processing_reports = set()
            self._processing_reports.add(report_id)

            recipients = set(self.active_users)
            recipients.add(self.group_id)
            recipients_list = list(recipients)

        try:
            logging.info(
                f'Отправка отчета {project_name} '
                f'пользователям: {recipients_list}'
            )
            sent_messages = set()

            for chat_id in recipients_list:
                try:
                    message_key = f'{project_name}_{chat_id}'

                    if message_key in sent_messages:
                        logging.debug(
                            f'Сообщение {message_key} '
                            'уже отправлено в этом отчете'
                        )
                        continue

                    logging.info(
                        f'Отправка отчёта {project_name} '
                        f'пользователю {chat_id}'
                    )
                    if 'SUCCESS' in tag:
                        self.get_robot(LIKE_ROBOT, chat_id)
                    else:
                        self.get_robot(DISSLIKE_ROBOT, chat_id)
                    self.send_message_str(chat_id, result)
                    sent_messages.add(message_key)

                    logging.info(f'Отчет отправлен пользователю {chat_id}')

                except Exception as e:
                    logging.error(f'Пользователь {chat_id} недоступен: {e}')
        finally:
            with self.lock:
                if hasattr(
                    self,
                    '_processing_reports'
                ) and report_id in self._processing_reports:
                    self._processing_reports.remove(report_id)

    def setup_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def wake_up(message):
            chat = message.chat
            chat_id = chat.id
            chat_type = chat.type
            self.active_users.add(chat_id)
            name = chat.first_name
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button_check = types.KeyboardButton('/logs')
            keyboard.add(button_check)
            message_str = 'Привет всем, я i-bot! Спасибо, что включили меня!'
            self.get_robot(HI_ROBOT, chat_id)
            if chat_type in ['group', 'supergroup']:
                self.send_message_str(chat_id, message_str, keyboard)
            else:
                message_str = (
                    f'Привет, я i-bot! Спасибо, что включил меня, {name}!'
                )
                self.send_message_str(chat_id, message_str, keyboard)

        @self.bot.message_handler(commands=['logs'])
        def check_project(message):
            try:
                chat_id = message.chat.id
                keyboard = types.ReplyKeyboardMarkup(
                    resize_keyboard=True,
                    row_width=len(PROJECTS)
                )
                for project_key in PROJECTS.keys():
                    keyboard.add(types.KeyboardButton(f'/check {project_key}'))
                back_button = types.KeyboardButton('/back')
                keyboard.add(back_button)
                message_str = 'Выбери проект для проверки логов:'
                self.send_message_str(chat_id, message_str, keyboard)
            except Exception as e:
                logging.error(f'Ошибка {e}')

        @self.bot.message_handler(commands=['check'])
        def show_project_logs(message):
            try:
                chat_id = message.chat.id
                project_name = message.text.split(' ', 1)[1]
                tag, result = self.log_monitor.check_logs(project_name)
                if not result:
                    logging.error('Ошибка мониторщик логов не отработал')
                    raise ValueError
                keyboard = types.ReplyKeyboardMarkup(
                    resize_keyboard=True,
                    row_width=len(PROJECTS)
                )
                for project_key in PROJECTS.keys():
                    keyboard.add(types.KeyboardButton(f'/check {project_key}'))
                back_button = types.KeyboardButton('/back')
                keyboard.add(back_button)
                if 'SUCCESS' in tag:
                    self.get_robot(LIKE_ROBOT, chat_id)
                else:
                    self.get_robot(DISSLIKE_ROBOT, chat_id)
                self.send_message_str(chat_id, result, keyboard)
            except Exception as e:
                logging.error(f'Ошибка {e}')

        @self.bot.message_handler(commands=['back'])
        def back_to_main(message):
            try:
                chat = message.chat
                chat_id = chat.id
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                button_check = types.KeyboardButton('/logs')
                keyboard.add(button_check)
                message_str = 'Главное меню:'
                self.send_message_str(chat_id, message_str, keyboard)
            except Exception as e:
                logging.error(f'Ошибка {e}')
