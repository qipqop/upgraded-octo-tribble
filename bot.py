
import asyncio

from loader import bot, dp
import logger

from handlers import commands, messages
from utils.middleware import MessageLogging, CallbackLogging

# Настройка логирования
botLogger = logger.get_logger('bot')

# Основная функция для инициализации и запуска бота


async def main() -> None:
    # Обработчики
    dp.message.middleware(MessageLogging())
    dp.callback_query.outer_middleware(CallbackLogging())
    dp.include_router(commands.commandRouter)
    dp.include_router(messages.userRouter)
    botLogger.info("Бот запущен!")
    await dp.start_polling(bot)


# Точка входа в программу
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        botLogger.info("Бот остановлен вручную!")
    finally:
        botLogger.info("Сессия закрыта.")
