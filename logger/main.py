import os

from dotenv import load_dotenv

from logger.bot import IBotLog

load_dotenv()


def main():
    bot = IBotLog(os.getenv('TELEGRAM_TOKEN'))

    if os.getenv('USE_WEBHOOK').lower() == 'true':
        bot.run_webhook()
    else:
        bot.run_polling()


if __name__ == '__main__':
    main()
