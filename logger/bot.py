import logging
import os
import random
import threading
import time
from collections import defaultdict
from datetime import datetime as dt

import requests
import schedule
from dotenv import load_dotenv
from telebot import TeleBot, types
from watchdog.observers import Observer

from logger.ai_agent import LlmAgent, model
from logger.check_files import FileChecker
from logger.check_ftp import FtpChecker
from logger.constants import (COFFE_ROBOT, COUNT_ROBOT, DATE_FORMAT,
                              ERROR_ROBOTS, GNEWS_URL, HI_ROBOT, HOST, MEMES,
                              OFF_PROJECTS, PASSWORD, PROJECTS,
                              SEND_MESSAGE_RETRIES, SUCCESS_ROBOTS,
                              TIME_FOR_ALLERT, USERNAME)
from logger.filewatch import WatchLog
from logger.log_checker import LogChecker
from logger.logging_config import setup_logging

setup_logging()
load_dotenv()


class IBotLog:
    """Класс управления телеграм-ботом."""

    def __init__(
        self,
        token: str,
        group_id=os.getenv('GROUP_ID'),
        log_checker=None
    ):
        self.token = token
        self.log_checker = log_checker or LogChecker()
        self.bot = TeleBot(token)
        self.group_id = int(group_id)
        self.active_users: set = set()
        self.log_observer = None
        self.report_message_count: dict[str, int] = defaultdict(int)
        self.success_scripts_name: set = set()
        self.setup_handlers()
        self.setup_file_watcher()
        self.start_daily_scheduler()

    def start_daily_scheduler(self):
        """
        Запускает ежедневную отправку в 10:00 сообщения
        о количестве полученных отчетов отработки скриптов.
        """
        def send_morning_message():

            dont_work_projects = []
            date_today = dt.now().strftime(DATE_FORMAT)
            day_of_week = dt.now().isoweekday()
            wish_text = 'Хорошего рабочего дня!'
            if day_of_week in (6, 7):
                wish_text = 'Хороших выходных!'
            for name, _ in PROJECTS.items():
                if name in OFF_PROJECTS:
                    continue
                if name not in self.success_scripts_name:
                    dont_work_projects.append(name)

            projects_count = len(PROJECTS) - len(OFF_PROJECTS)
            offed_projects_report = (
                'Отключенные или не попадающие '
                f'в отбивку проекты: {OFF_PROJECTS}'
            )

            success_message_text = (
                f'Отработали все {self.report_message_count[date_today]}/'
                f'{projects_count} скриптов. {offed_projects_report}. '
                f'{wish_text}'
            )
            failure_message_text = (
                'Отработали не все скрипты: '
                f'{self.report_message_count[date_today]}/'
                f'{projects_count}. Не было сообщений по скриптам: '
                f'{dont_work_projects}. {offed_projects_report}. '
                'Не лучшее начало дня, но вы справитесь!'
            )
            self.success_scripts_name.clear()
            self.active_users.add(self.group_id)
            for chat_id in list(self.active_users):
                try:
                    if self.report_message_count[date_today] == projects_count:
                        self.get_robot(COFFE_ROBOT, chat_id)
                        self.send_message_str(chat_id, success_message_text)
                    else:
                        self.get_robot(COUNT_ROBOT, chat_id)
                        self.send_message_str(chat_id, failure_message_text)

                    checker_file = FileChecker()
                    messages_old_feeds = checker_file.check_files()
                    message_old_feed = (
                        'Сводка по обновлению скачанных файлов:\n'
                    )
                    if messages_old_feeds:
                        for i, line in enumerate(messages_old_feeds, 1):
                            message_old_feed += f'{i}. {line}\n'
                        self.send_message_str(chat_id, message_old_feed)
                    else:
                        message_old_feed += (
                            'А нет сводки! Что-то пошло не так('
                        )
                        self.send_message_str(chat_id, message_old_feed)

                    if all([HOST, USERNAME, PASSWORD]):
                        checker_ftp = FtpChecker(HOST, USERNAME, PASSWORD)
                        messages_ftp_feeds = checker_ftp.check_new_files()
                        message_new_feed = (
                            'Сводка по обновлению файлов на FTP:\n'
                        )
                        if messages_ftp_feeds:
                            for i, line in enumerate(messages_ftp_feeds, 1):
                                message_new_feed += f'{i}. {line}\n'
                            self.send_message_str(chat_id, message_new_feed)
                        else:
                            message_new_feed += (
                                'А нет сводки! Что-то пошло не так('
                            )
                            self.send_message_str(chat_id, message_new_feed)

                    news_list = self.get_news()
                    if not news_list:
                        continue
                except Exception as error:
                    logging.error(
                        'Ошибка отправки утреннего сообщения: %s',
                        error
                    )
                try:
                    message_news_text = '📰 Немного новостей вам:\n\n'
                    for i, news in enumerate(news_list, 1):
                        message_news_text += (
                            f"{i}. {news['description']}\n{news['url']}\n\n"
                        )
                    self.send_message_str(chat_id, message_news_text)
                except Exception as error:
                    logging.error(
                        'Не удалось отправить новостное сообщение: %s',
                        error
                    )
            self.report_message_count.clear()
        schedule.every().day.at(TIME_FOR_ALLERT).do(send_morning_message)

        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)

        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()

    def get_news(self) -> list:
        apikey = os.getenv('GNEWS_API_KEY')
        if not apikey:
            return []
        url = GNEWS_URL
        params = {
            'category': 'general',
            'lang': 'ru',
            'country': 'ru',
            'max': '5',
            'apikey': apikey
        }
        return requests.get(url, params=params).json()['articles']

    def get_robot(self, robot, chat_id, robot_folder='robot'):
        try:
            with open(f'{robot_folder}/{robot}', 'rb') as photo:
                self.bot.send_sticker(chat_id, photo, timeout=60)
        except FileNotFoundError:
            logging.warning('Робот %s не найден', robot)
        except Exception as error:
            logging.error('Неожиданная ошибка: %s', error)

    def send_message_str(self, chat_id, message_str, keyboard=None):
        retries = SEND_MESSAGE_RETRIES

        for attempt in range(1, retries + 1):
            try:
                self.bot.send_message(
                    chat_id=chat_id,
                    text=message_str,
                    reply_markup=keyboard,
                    timeout=60
                )
                logging.info('Сообщение отправлено получателю %s', chat_id)
                return
            except Exception as error:
                logging.error(
                    'Ошибка отправки (попытка %s/%s) для %s: %r',
                    attempt,
                    retries,
                    chat_id,
                    error
                )
                if attempt == retries:
                    raise
                time.sleep(2)

    def setup_file_watcher(self):
        self.log_observer = Observer()
        event_handler = WatchLog(self)

        for project_config in PROJECTS.values():
            log_dir = project_config['log_path']
            self.log_observer.schedule(
                event_handler,
                log_dir,
                recursive=True
            )

        self.log_observer.start()

    def send_project_report(self, project_name: str):
        tag, result = self.log_checker.check_logs(project_name)
        logging.info(
            'send_project_report вызван для %s, tag=%s',
            project_name,
            tag
        )

        if tag in ['PENDING', 'WARNING', 'NOTFOUND']:
            return

        self.active_users.add(self.group_id)
        logging.info('Активные пользователи: %s', list(self.active_users))

        for chat_id in list(self.active_users):
            try:
                logging.info(
                    'Отправка отчёта %s пользователю %s',
                    project_name,
                    chat_id
                )

                if 'SUCCESS' in tag:
                    rndm_success_robot = random.choice(SUCCESS_ROBOTS)
                    self.get_robot(rndm_success_robot, chat_id)
                else:
                    rndm_error_robot = random.choice(ERROR_ROBOTS)
                    self.get_robot(rndm_error_robot, chat_id)

                date_today = dt.now().strftime(DATE_FORMAT)
                self.send_message_str(chat_id, result)
                self.success_scripts_name.add(project_name)
                self.report_message_count[date_today] += 1
                logging.info('Отчет отправлен пользователю %s', chat_id)

            except Exception as error:
                self.active_users.discard(chat_id)
                logging.error('Пользователь %s недоступен: %s', chat_id, error)

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
            except Exception as error:
                logging.error('Ошибка %s', error)

        @self.bot.message_handler(commands=['check'])
        def show_project_logs(message):
            try:
                chat_id = message.chat.id
                project_name = message.text.split(' ', 1)[1]
                tag, result = self.log_checker.check_logs(project_name)
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
                    rndm_success_robot = random.choice(SUCCESS_ROBOTS)
                    self.get_robot(rndm_success_robot, chat_id)
                else:
                    rndm_error_robot = random.choice(ERROR_ROBOTS)
                    self.get_robot(rndm_error_robot, chat_id)
                self.send_message_str(chat_id, result, keyboard)
            except Exception as error:
                logging.error('Ошибка %s', error)

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
            except Exception as error:
                logging.error('Ошибка %s', error)

        @self.bot.message_handler(commands=['memes'])
        def show_memes(message):
            chat = message.chat
            chat_id = chat.id
            random_memes = random.choice(MEMES)
            self.get_robot(random_memes, chat_id, 'easteregg')

        @self.bot.message_handler(
            content_types=['text'],
            func=lambda m: (
                m.text
                and 'i-bot' in m.text.lower()
                and not m.text.strip().startswith('/')
            )
        )
        def handle_i_bot_request(message):
            try:
                logging.info('Сработал хендлер на i-bot')
                chat_id = message.chat.id
                text = message.text.lower()
                after_trigger = text.split('i-bot', 1)[1].strip()
                user_query = after_trigger.lstrip(' ,.:;-')
                agent = LlmAgent(model)
                response = agent.ask(user_query)
                logging.info('Получен ответ: %s', response)
                self.send_message_str(chat_id, str(response)[:4000])
                logging.info('Сообщение отправлено в чат: %s', chat_id)
            except Exception as error:
                logging.error('Ошибка в handle_i_bot_request: %s', error)
                self.send_message_str(chat_id, '')
