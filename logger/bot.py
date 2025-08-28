import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from telebot import TeleBot, types

from logger.constants import PROJECTS
from logger.logging_config import setup_logging
from logger.utils import LogMonitor

setup_logging()


class IBotLog:

    def __init__(self, token: str, log_monitor=None):
        self.log_monitor = log_monitor or LogMonitor()
        self.bot = TeleBot(token)
        self.scheduler = BackgroundScheduler()
        self.active_users = set()
        self.setup_handlers()
        self.setup_daily_checks()

    def setup_daily_checks(self):
        for project_name, project_config in PROJECTS.items():
            check_time = project_config.get('check_time', '09:00')
            hour, minute = map(int, check_time.split(':'))
            self.scheduler.add_job(
                self.send_project_report,
                trigger=CronTrigger(
                    hour=hour,
                    minute=minute,
                    timezone='Europe/Moscow'
                ),
                args=[project_name],
                id=f'check_{project_name}'
            )
        self.scheduler.start()

    def send_project_report(self, project_name: str):
        result = self.log_monitor.check_logs(project_name)
        for chat_id in list(self.active_users):
            try:
                self.bot.send_message(chat_id, result)
                if 'SUCCESS' in result:
                    try:
                        with open('robot/like-robot.jpg', 'rb') as photo:
                            self.bot.send_photo(chat_id, photo)
                    except FileNotFoundError:
                        logging.warning('Робот like-robot не найден')
                else:
                    try:
                        with open('robot/disslike-robot.png', 'rb') as photo:
                            self.bot.send_photo(chat_id, photo)
                    except FileNotFoundError:
                        logging.warning('Робот disslike-robot не найден')
            except Exception as e:
                logging.error(f'Пользователь {chat_id} недоступен: {e}')
                self.active_users.discard(chat_id)

    def setup_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def wake_up(message):
            chat = message.chat
            chat_id = chat.id
            self.active_users.add(chat_id)
            name = chat.first_name
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button_check = types.KeyboardButton('/logs')
            keyboard.add(button_check)

            self.bot.send_message(
                chat_id=chat_id,
                text=f'Привет, я i-bot! Спасибо, что включил меня, {name}!',
                reply_markup=keyboard
            )
            try:
                with open('robot/hi-robot.jpg', 'rb') as photo:
                    self.bot.send_photo(chat_id=chat_id, photo=photo)
            except FileNotFoundError:
                logging.warning('Робот hi-robot не найден')

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

                self.bot.send_message(
                    chat_id=chat_id,
                    text='Выбери проект для проверки логов:',
                    reply_markup=keyboard
                )
            except Exception as e:
                logging.error(f'Ошибка {e}')

        @self.bot.message_handler(commands=['check'])
        def show_project_logs(message):
            try:
                chat_id = message.chat.id
                project_name = message.text.split(' ', 1)[1]
                result = self.log_monitor.check_logs(project_name)
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

                self.bot.send_message(
                    chat_id=chat_id,
                    text=result,
                    reply_markup=keyboard
                )
                if 'SUCCESS' in result:
                    try:
                        with open('robot/like-robot.jpg', 'rb') as photo:
                            self.bot.send_photo(chat_id=chat_id, photo=photo)
                    except FileNotFoundError:
                        logging.warning('Робот like-robot не найден')
                else:
                    try:
                        with open('robot/disslike-robot.png', 'rb') as photo:
                            self.bot.send_photo(chat_id=chat_id, photo=photo)
                    except FileNotFoundError:
                        logging.warning('Робот disslike-robot не найден')
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

                self.bot.send_message(
                    chat_id=chat_id,
                    text='Главное меню:',
                    reply_markup=keyboard
                )
            except Exception as e:
                logging.error(f'Ошибка {e}')

        @self.bot.message_handler(
            func=lambda m: m.text and m.text.startswith('DEPLOY')
        )
        def deploy_success(message):
            full_text = message.text
            project_name = 'проекта'
            if full_text.split()[1] in PROJECTS:
                project_name = full_text.split()[1]
            try:
                with open('robot/deploy-robot.png', 'rb') as photo:
                    self.bot.send_photo(chat_id=message.chat.id, photo=photo)
            except FileNotFoundError:
                logging.warning('Робот deploy-robot не найден')
            self.bot.send_message(
                chat_id=message.chat.id,
                text=f'✅ Деплой {project_name} успешно выполнен!'
            )
            for chat_id in self.active_users:
                if chat_id != message.chat.id:
                    try:
                        with open('robot/deploy-robot.png', 'rb') as photo:
                            self.bot.send_photo(chat_id=chat_id, photo=photo)
                    except FileNotFoundError:
                        logging.warning('Робот deploy-robot не найден')

                    self.bot.send_message(
                        chat_id=chat_id,
                        text=f'✅ Деплой {project_name} успешно выполнен!'
                    )

    def run(self):
        self.bot.polling()
