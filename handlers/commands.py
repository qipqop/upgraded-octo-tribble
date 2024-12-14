from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile

import config
from utils.database import AsyncDatabaseManager
from handlers import texts as UM
from keyboards import reply as RK, inline as IK
from utils.states import UserStatus
from sheet import get_order, get_new_data
import logger

commandRouter = Router()
botLogger = logger.get_logger('bot')
commandRouter.name = 'commandRouter'
dbManager = AsyncDatabaseManager(config.db_config)


@commandRouter.message(Command("start"))
async def welcome(message: Message, state: FSMContext, command: Command = None) -> None:
    await state.set_state(UserStatus.usual)

    # Добавляем пользователя в базу данных
    await dbManager.dbUsers.add_user(user_data={
        'userTgID': message.from_user.id,
        'userChatID': message.chat.id,
        'userTgUsername': message.from_user.username,
    })

    # Проверка наличия UTM-метки (например, payload)
    utm_data = {}
    if message.text and " " in message.text:
        command_args = message.text.split(" ", 1)[1]  # Извлекаем данные после /start
        utm_data = parse_utm(command_args)  # parse_utm - функция для парсинга UTM данных

    # Логирование или сохранение UTM-меток, если они есть
    if utm_data:
        botLogger.info(f"Получены UTM данные: {utm_data}")

    # Проверка наличия payload и статуса заказа
    if 'payload' in utm_data:
        payload = utm_data['payload']

        # Получаем текущие данные пользователя из состояния
        state_data = await state.get_data()
        orders = state_data.get('orders', [])

        # Ищем заказ по payload
        order = next((order for order in orders if order['payload'] == payload), None)

        if order:
            try:
                await message.answer("⚙️ Проверяю оплату...")
                if order['status'] == "process":
                    # Сохраняем изменения в состояние
                    await state.update_data(orders=orders)
                    # Отправляем уведомление о том, что заказ оплачен
                    token = get_order(name=order['name'], userID=message.chat.id)
                    if token:
                        order['status'] = "paid"
                        # Сохраняем обновленный список в состоянии
                        await state.update_data(orders=orders)
                        await message.answer(f"<b>🎉 Ваш заказ оплачен</b>\n\n{token}")
                        # Обновляем статус заказа на "оплачен"
                    else:
                        await message.answer("Произошла ошибка при обработке заказа.")
                elif order['status'] == "paid":
                    # Если заказ уже оплачен
                    await message.answer("Этот заказ уже был оплачен ранее.")
                else:
                    await message.answer("Неизвестный статус заказа.")
            except KeyError as e:
                botLogger.error(f"Ошибка при обработке статуса заказа: {e}")
                await message.answer("Не удалось найти заказ с таким payload.")
            except Exception as e:
                botLogger.error(f"Неизвестная ошибка при обработке заказа: {e}")
                await message.answer("Произошла ошибка при обработке заказа. Попробуйте снова позже.")
        else:
            await message.answer("Не удалось найти заказ с таким payload.")

    # Отправка приветственного сообщения
    welcomeText = UM.welcome.format(
        first_name=message.from_user.first_name if message.from_user.first_name else '',
        last_name=message.from_user.last_name if message.from_user.last_name else '',
    )
    await message.answer(welcomeText, reply_markup=IK.mainMenu)

def parse_utm(command_args: str) -> dict:
    """
    Функция для парсинга UTM-меток из строки, например, '/start payload=<payload_value>'
    Возвращает словарь с UTM-данными
    """
    utm_data = {}
    args = command_args.split(' ')
    for arg in args:
        if '=' in arg:
            key, value = arg.split('=', 1)
            utm_data[key] = value
    return utm_data



@commandRouter.message(Command("update"))
async def welcome(message: Message, state: FSMContext, command: Command = None) -> None:
    await state.set_state(UserStatus.usual)
    await message.answer('Обновляю данные...')
    get_new_data()
    await message.answer('Данные таблицы обновлены')
