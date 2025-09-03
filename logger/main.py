import os
from dotenv import load_dotenv
from logger.bot import IBotLog
from logger.webhook import WebhookManager

load_dotenv()

bot = IBotLog(os.getenv('TELEGRAM_TOKEN'))
webhook_manager = WebhookManager(
    bot=bot,
    host=os.getenv('WEBHOOK_HOST')
)

app = webhook_manager.get_app()
