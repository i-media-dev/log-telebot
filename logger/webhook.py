import logging
import ssl

from flask import Flask, request
from telebot import types
import os

from logger.logging_config import setup_logging

setup_logging()


class WebhookManager:

    def __init__(
        self,
        bot,
        host: str = None,
        port: int = 8443,
        ssl_cert_path: str = None,
        ssl_key_path: str = None
    ):
        self.bot = bot
        self.host = host or os.getenv('WEBHOOK_HOST')
        self.port = port or int(os.getenv('WEBHOOK_PORT'))
        self.ssl_cert_path = ssl_cert_path or os.getenv('SSL_CERT_PATH')
        self.ssl_key_path = ssl_key_path or os.getenv('SSL_KEY_PATH')
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
        try:
            self.bot.remove_webhook()
            webhook_url = f'https://{self.host}:{self.port}/{self.bot.token}/'
            self.bot.set_webhook(url=webhook_url)
            logging.info(f'Webhook установлен: {webhook_url}')
        except Exception as e:
            logging.error(f'Ошибка установки webhook: {e}')
            raise

    def start(self):
        ssl_context = None
        if self.ssl_cert_path and self.ssl_key_path:
            ssl_context = (self.ssl_cert_path, self.ssl_key_path)
        self.app.run(host='0.0.0.0', port=self.port)
