import logging

from flask import Flask, request
from telebot import types
import os

from logger.constants import DEPLOY_ROBOT
from logger.logging_config import setup_logging

setup_logging()


class WebhookManager:

    def __init__(
        self,
        bot,
        telebot,
        host: str = None
    ):
        self.bot = bot
        self.telebot = telebot
        self.host = host or os.getenv('WEBHOOK_HOST')
        self.app = Flask(__name__)
        self._setup_routes()
        self._setup_webhook()

    def _setup_routes(self):
        @self.app.route(f'/{self.bot.token}/', methods=['POST'])
        def webhook():
            json_string = request.get_data().decode('utf-8')
            update = types.Update.de_json(json_string)
            self.bot.process_new_updates([update])
            return 'OK'

        @self.app.route('/trigger_deploy', methods=['POST'])
        def trigger_deploy():
            data = request.json
            project_name = data.get('project', 'проекта')

            message_str = f'✅ Деплой {project_name} успешно выполнен!'
            if project_name == 'log-telebot':
                message_str = f'✌ Я обновился!'

            self.bot.send_message_str(os.getenv('TELEGRAM_TO'), message_str)
            self.bot.get_robot(DEPLOY_ROBOT, os.getenv('TELEGRAM_TO'))

            for user_id in self.bot.active_users:
                self.bot.send_message_str(user_id, message_str)
                self.bot.get_robot(DEPLOY_ROBOT, user_id)
            return 'OK'

    def _setup_webhook(self):
        webhook_url = f'https://{self.host}/{self.bot.token}/'
        try:
            info = self.telebot.get_webhook_info()
            if info.url != webhook_url:
                self.telebot.remove_webhook()
                self.telebot.set_webhook(url=webhook_url)
                logging.info(f'Webhook обновлён: {webhook_url}')
            else:
                logging.info(f'Webhook уже установлен: {webhook_url}')
        except Exception as e:
            logging.error(f'Ошибка установки webhook: {e}')

    def get_app(self):
        return self.app
