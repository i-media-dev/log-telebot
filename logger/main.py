import os

from dotenv import load_dotenv

from logger.bot import IBotLog
from logger.webhook import WebhookManager

load_dotenv()


def main():
    bot = IBotLog(os.getenv('TELEGRAM_TOKEN'))
    webhook_manager = WebhookManager(
        bot=bot,
        telebot=bot.bot,
        host=os.getenv('WEBHOOK_HOST')
    )

    webhook_manager.setup_webhook()
    return webhook_manager.get_app()


if __name__ == '__main__':
    app = main()
