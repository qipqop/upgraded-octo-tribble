from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.types import Message, CallbackQuery, FSInputFile,  ContentType
import random
import logger

import config
from handlers import texts as UM
from utils.states import UserStatus
from utils.database import AsyncDatabaseManager
from keyboards import reply as RK, inline as IK
from payment import create_order
from utils.filters import IsDigit, IsText, TextFilter
from handlers.JsonDispatcher import get_sub_structure, get_price_data

userRouter = Router()
userRouter.name = 'userRouter'

botLogger = logger.get_logger('bot')

dbManager = AsyncDatabaseManager(config.db_config)


# ==========================================
# БЛОК: Отмена
# ==========================================

@userRouter.callback_query(F.data.startswith("delMess"))  # Кнопка: Закрыть
async def handleEscapeCall(query: CallbackQuery, state: FSMContext) -> None:
    await query.message.delete()
    await state.set_state(UserStatus.usual)
    await query.answer()


@userRouter.message(TextFilter("Отменить"))  # Кнопка: Отменить
async def handleEscapeMess(message: Message, state: FSMContext) -> None:
    await state.set_state(UserStatus.usual)
    await message.answer(UM.mainMenu, reply_markup=RK.mainMenu)


# ==========================================
# БЛОК: Главное меню
# ==========================================

@userRouter.callback_query(F.data.startswith("mainMenu"))  # Кнопка: Гл меню
async def handleMainMenuCall(query: CallbackQuery, state: FSMContext) -> None:
    await query.message.delete()
    await query.message.answer(text=UM.mainMenu, reply_markup=IK.mainMenu)
    await query.answer()


@userRouter.callback_query(F.data.startswith("openMagaz"))  # Кнопка: Открыть меню
async def handleMainMenuCall(query: CallbackQuery, state: FSMContext) -> None:
    await query.message.delete()
    await query.message.answer(UM.category_choise, reply_markup= await IK.generate_first_category())
    await query.answer()

@userRouter.callback_query(F.data.startswith("cat_"))
async def handle_item_selection(query: CallbackQuery, state: FSMContext):
    try:
        # Удаляем предыдущее сообщение
        await query.message.delete()

        # Извлекаем текст кнопки
        button_text = None
        for row in query.message.reply_markup.inline_keyboard:
            for button in row:
                if button.callback_data == query.data:
                    button_text = button.text
                    break

        # Генерируем клавиатуру для выбранной категории
        keyboard = IK.generate_menu(
            category_name=button_text,
            sub_structure=config.menu_structure
        )

        # Обновляем состояние пользователя с выбранной категорией
        await state.update_data(fitstCat=button_text)

        # Отправляем сообщение с клавиатурой
        await query.message.answer(UM.category_choise, reply_markup=keyboard)

        # Подтверждаем callback
        await query.answer()

    except Exception as e:
        # Логирование ошибки
        botLogger.error(f"Ошибка при обработке запроса на категорию: {e}")

        # Отправляем сообщение с ошибкой и возвращаем пользователя в главное меню
        await query.message.answer(
            "Произошла ошибка. Попробуйте позже.",
            reply_markup=IK.mainMenu  # Главное меню
        )
        await query.answer()


@userRouter.callback_query(F.data.startswith("subca_"))
async def handle_item_selection(query: CallbackQuery, state: FSMContext):
    try:
        await query.message.delete()

        # Извлекаем данные из состояния
        userData = await state.get_data()
        fitstCat = userData['fitstCat']
        button_text = None

        # Находим текст кнопки
        for row in query.message.reply_markup.inline_keyboard:
            for button in row:
                if button.callback_data == query.data:
                    button_text = button.text
                    break

        # Получаем данные подкатегории
        sub_data = get_sub_structure()[f'{button_text}']
        sub_structure = {
            f'{button_text}': sub_data
        }

        # Генерируем клавиатуру с подкатегориями
        keyboard = IK.generate_menu(
            category_name=button_text,
            sub_structure=sub_structure,
        )

        # Обновляем состояние
        await state.update_data(secondCat=button_text)

        # Отправляем сообщение пользователю
        await query.message.answer(UM.subcategory_choise.format(path=f"{fitstCat} > {button_text}"), reply_markup=keyboard)
        await query.answer()

    except Exception:  # Обработка ошибки, если подкатегория не найдена
        await query.message.answer(
            "Товар по этой категории закончился.",
            reply_markup=IK.mainMenu  # Отправляем главное меню
        )
        await query.answer()

@userRouter.callback_query(F.data.startswith("item_"))
async def handle_item_selection(query: CallbackQuery, state: FSMContext):
    try:
        # Удаляем предыдущее сообщение
        await query.message.delete()

        # Извлекаем текст кнопки
        button_text = None
        for row in query.message.reply_markup.inline_keyboard:
            for button in row:
                if button.callback_data == query.data:
                    button_text = button.text
                    break

        # Получаем цену товара
        price_data = get_price_data()
        if button_text not in price_data:
            await query.answer("Ошибка: Товар не найден.", show_alert=True)
            return
        curs = price_data['curs']
        price = int(price_data[button_text]) / int(curs)

        # Генерируем уникальный payload
        random_digits = ''.join(random.choices('0123456789', k=5))
        payload = f"{query.message.chat.id}_{random_digits}"

        # Создаем заказ
        invoice = create_order(payload=payload, price=price)
        botLogger.info(f"Создан заказ: {invoice}")

        # Обновляем словарь заказов в состоянии
        state_data = await state.get_data()
        orders = state_data.get('orders', [])  # Получаем текущие заказы или пустой список

        # Добавляем новый заказ в список
        orders.append({
            "name": button_text,
            "payload": payload,
            "status": "process"
        })

        # Сохраняем обновленный список в состоянии
        await state.update_data(orders=orders)

        # Отправляем пользователю информацию о заказе
        await query.message.answer(
            text=UM.itemCap.format(item_name=button_text, price=price),
            reply_markup=await IK.itemMenu(invoice['pay_url'])
        )

        # Подтверждаем callback
        await query.answer()

    except Exception as e:
        # Логирование ошибки
        botLogger.error(f"Ошибка при обработке заказа: {e}")

        # Отправляем сообщение об ошибке и возвращаем пользователя в главное меню
        await query.message.answer(
            "Произошла ошибка при обработке заказа. Попробуйте позже.",
            reply_markup=IK.mainMenu  # Главное меню
        )
        await query.answer()


@userRouter.callback_query(F.data.startswith("backSub"))
async def handle_item_selection(query: CallbackQuery, state: FSMContext):
    try:
        # Удаляем предыдущее сообщение
        await query.message.delete()

        # Получаем данные пользователя из состояния
        userData = await state.get_data()
        fitstCat = userData['fitstCat']
        secondCat = userData['secondCat']

        # Получаем подкатегории для второго уровня
        sub_data = get_sub_structure().get(f'{secondCat}')
        if not sub_data:
            raise ValueError(f"Подкатегории для {secondCat} не найдены.")

        # Формируем структуру подкатегории
        sub_structure = {f'{secondCat}': sub_data}

        # Генерируем клавиатуру для подкатегории
        keyboard = IK.generate_menu(
            category_name=secondCat,
            sub_structure=sub_structure,
        )

        # Отправляем сообщение с клавиатурой
        await query.message.answer(UM.subcategory_choise.format(path=f"{fitstCat} > {secondCat}"), reply_markup=keyboard)
        await query.answer()

    except ValueError as e:
        # Логирование ошибки
        botLogger.error(f"Ошибка: {e}")

        # Отправляем сообщение об ошибке и возвращаем пользователя в главное меню
        await query.message.answer(
            "Произошла ошибка при получении подкатегорий. Попробуйте позже.",
            reply_markup=IK.mainMenu  # Главное меню
        )
        await query.answer()

    except Exception as e:
        # Логирование общей ошибки
        botLogger.error(f"Ошибка при обработке запроса: {e}")

        # Отправляем сообщение об ошибке и возвращаем пользователя в главное меню
        await query.message.answer(
            "Произошла ошибка. Попробуйте позже.",
            reply_markup=IK.mainMenu  # Главное меню
        )
        await query.answer()

@userRouter.callback_query(F.data == "back_to_categories")
async def handle_back_to_categories(query: CallbackQuery, state: FSMContext):
    try:
        # Удаляем предыдущее сообщение
        await query.message.delete()

        # Отправляем сообщение с основным меню
        await query.message.answer(UM.category_choise, reply_markup=await IK.generate_first_category())

        # Подтверждаем callback
        await query.answer()

    except Exception as e:
        # Логирование ошибки
        botLogger.error(f"Ошибка при обработке запроса на возврат в категории: {e}")

        # Отправляем сообщение с ошибкой и возвращаем пользователя в главное меню
        await query.message.answer(
            "Произошла ошибка. Попробуйте позже.",
            reply_markup=IK.mainMenu  # Главное меню
        )
        await query.answer()
