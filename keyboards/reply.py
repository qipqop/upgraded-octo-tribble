from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup as RKM, KeyboardButton as RB


# Удаление клавиатуры пользователя
removeKeyboard = ReplyKeyboardRemove()

# Клавиатура отмены текущего действия и перехода в меню
escape = RKM(
    keyboard=[
        [RB(text="Отменить")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)
