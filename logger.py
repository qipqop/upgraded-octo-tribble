import logging
from logging.handlers import RotatingFileHandler
import os

# Создаем директорию для логов, если ее нет
log_dir = os.path.join(os.path.dirname(__file__), './logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Настройка логгера для логов по работе бота
bot_logger = logging.getLogger('bot')
bot_logger.setLevel(logging.DEBUG)

# Создаем обработчик для ротации файлов
bot_handler = RotatingFileHandler(
    os.path.join(log_dir, 'bot.log'),
    maxBytes=5*1024*1024,  # 5 MB
    backupCount=5  # Хранить 5 архивных файлов
)
bot_handler.setLevel(logging.DEBUG)
bot_formatter = logging.Formatter(
    '#%(levelname)-3s [%(asctime)s] - %(message)s')
bot_handler.setFormatter(bot_formatter)
bot_logger.addHandler(bot_handler)

# Настройка логгера для логов сообщений пользователей в боте
messages_logger = logging.getLogger('messages')
messages_logger.setLevel(logging.DEBUG)

# Создаем обработчик для ротации файлов
messages_handler = RotatingFileHandler(
    os.path.join(log_dir, 'messages.log'),
    maxBytes=5*1024*1024,  # 5 MB
    backupCount=5  # Хранить 5 архивных файлов
)
messages_handler.setLevel(logging.DEBUG)
messages_formatter = logging.Formatter(
    '#%(levelname)-3s [%(asctime)s] - %(message)s')
messages_handler.setFormatter(messages_formatter)
messages_logger.addHandler(messages_handler)


def get_logger(name):
    if name == 'bot':
        return bot_logger
    elif name == 'messages':
        return messages_logger
    else:
        raise ValueError(f"Данного логгера нет: {name}")
