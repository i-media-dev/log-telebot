import os

from dotenv import load_dotenv

from logger.bot import IBotLog

load_dotenv()


def main():
    bot = IBotLog(os.getenv('TELEGRAM_TOKEN'))
    bot.run()


if __name__ == '__main__':
    main()
