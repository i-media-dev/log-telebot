import os
from dotenv import load_dotenv
from logger.bot import IBotLog
from logger.webhook import WebhookManager

load_dotenv()

bot = IBotLog(os.getenv('TELEGRAM_TOKEN'))
webhook_manager = WebhookManager(
    bot=bot,
    host=os.getenv('WEBHOOK_HOST'),
    port=int(os.getenv('WEBHOOK_PORT', 8443))
)
app = webhook_manager.get_app()

if __name__ == '__main__':
    webhook_manager.start()
