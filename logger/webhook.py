import logging

from flask import Flask, request
from telebot import types
import os

from logger.logging_config import setup_logging

setup_logging()


class WebhookManager:

    def __init__(
        self,
        bot,
        host: str = None
    ):
        self.bot = bot
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

    def _setup_webhook(self):
        webhook_url = f'https://{self.host}/{self.bot.token}/'
        try:
            info = self.bot.get_webhook_info()
            if info.url != webhook_url:
                self.bot.remove_webhook()
                self.bot.set_webhook(url=webhook_url)
                logging.info(f'Webhook обновлён: {webhook_url}')
            else:
                logging.info(f'Webhook уже установлен: {webhook_url}')
        except Exception as e:
            logging.error(f'Ошибка установки webhook: {e}')

    def get_app(self):
        """Метод для получения объекта Flask app для Gunicorn"""
        return self.app
