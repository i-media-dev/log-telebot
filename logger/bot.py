import logging

from telebot import TeleBot, types

from logger.constants import PROJECTS
from logger.logging_config import setup_logging
from logger.utils import LogMonitor

setup_logging()


class IBotLog:

    def __init__(self, token: str, log_monitor=None):
        self.log_monitor = log_monitor or LogMonitor()
        self.bot = TeleBot(token)
        self.setup_handlers()

    def setup_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def wake_up(message):
            chat = message.chat
            chat_id = chat.id
            name = chat.first_name
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button_check = types.KeyboardButton('/logs')
            keyboard.add(button_check)

            self.bot.send_message(
                chat_id=chat_id,
                text=f'Привет, я i-bot! Спасибо, что включил меня, {name}!',
                reply_markup=keyboard
            )
            with open('robot/hi-robot.jpg', 'rb') as photo:
                self.bot.send_photo(chat_id=chat_id, photo=photo)

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
                    with open('robot/like-robot.jpg', 'rb') as photo:
                        self.bot.send_photo(chat_id=chat_id, photo=photo)
                else:
                    with open('robot/disslike-robot.png', 'rb') as photo:
                        self.bot.send_photo(chat_id=chat_id, photo=photo)
            except Exception as e:
                logging.error(f'Ошибка {e}')

        @self.bot.message_handler(commands=['back'])
        def back_to_main(message):
            try:
                chat = message.chat
                chat_id = chat.id
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                button_check = types.KeyboardButton('/check')
                keyboard.add(button_check)

                self.bot.send_message(
                    chat_id=chat_id,
                    text='Главное меню:',
                    reply_markup=keyboard
                )
            except Exception as e:
                logging.error(f'Ошибка {e}')

    def run(self):
        self.bot.polling()
