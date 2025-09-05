import os
import threading

from dotenv import load_dotenv
from logger.bot import IBotLog
from logger.poller import Poller
from logger.webhook import WebhookManager

load_dotenv()

bot = IBotLog(os.getenv('TELEGRAM_TOKEN'))

poller = Poller(bot)
threading.Thread(target=poller.start, daemon=True).start()

webhook_manager = WebhookManager(
    bot=bot,
    telebot=bot.bot,
    host=os.getenv('WEBHOOK_HOST')
)

app = webhook_manager.get_app()
