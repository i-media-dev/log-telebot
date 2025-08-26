import os

from telebot import TeleBot, types

from dotenv import load_dotenv

from logger.constants import PROJECTS

load_dotenv()

bot = TeleBot(os.getenv('TELEGRAM_TOKEN'))


class LogMonitor:

    def __init__(self, projects: dict[str, str] = PROJECTS):
        self.projects = projects

    def check_logs(self, project_name: str) -> str:
        """Проверка логов проекта."""
        project = self.projects[project_name]
        if not os.path.exists(project['log_path']):
            return f'❌ Файл лога не найден: {project['log_path']}.'
        try:
            with open(project['log_path'], 'r', encoding='utf-8') as f:
                log_content = f.read()
        except Exception as e:
            return f'❌ Ошибка чтения лога: {str(e)}.'


@bot.message_handler(commands=['start'])
def wake_up(message):
    chat = message.chat
    chat_id = chat.id
    name = chat.first_name
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_start = types.KeyboardButton('/start')
    keyboard.add(button_start)
    bot.send_message(
        chat_id=chat_id,
        text=f'Привет, я i-bot! Спасибо, что включил меня, {name}!'
    )
    with open('robot/hi-robot.jpg', 'rb') as photo:
        bot.send_photo(chat_id=chat_id, photo=photo)


bot.polling()
