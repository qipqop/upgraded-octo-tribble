from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
import config
from aiogram.enums.parse_mode import ParseMode
from utils.customStorage import SQLiteStorage

# 5550125Pp

bot = Bot(token=config.botToken,default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
    ))
dp = Dispatcher(storage=SQLiteStorage(db_path='fsm.db'))
dp.name = 'mainDispatcher'
