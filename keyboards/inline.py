from aiogram.types import InlineKeyboardMarkup as IKM, InlineKeyboardButton as IB
from config import menu_structure
# =========================
# Статические клавиатуры
# =========================
mainMenu = IKM(
    inline_keyboard=[
        [IB(text="*Согласен принять условия", callback_data="openMagaz")],
    ],
    row_width=2
)

async def generate_first_category():
    """
    Генерирует объект InlineKeyboardMarkup на основе ключей menu_structure.

    :param menu_structure: Словарь с категориями и подкатегориями
    :return: Объект InlineKeyboardMarkup
    """
    keyboard = []
    i = 1
    for category in menu_structure.keys():
        keyboard.append([IB(text=category, callback_data=f"cat_{i}")])
        i += 1

    keyboard.append([IB(text="⬅️ Назад", callback_data="mainMenu")])
    IKkeyboard = IKM(
        inline_keyboard=keyboard,
        row_width=2
    )

    return IKkeyboard


def generate_menu(category_name, sub_structure,back_button="back_to_categories"):
    """
    Генерирует меню для подкатегорий и товаров.

    :param category_name: Название подкатегории.
    :param sub_structure: Словарь структуры подкатегорий и товаров.
    :return: Объект InlineKeyboardMarkup.
    """
    # Проверяем, есть ли такая подкатегория в структуре
    if category_name not in sub_structure:
        raise ValueError(f"Подкатегория '{category_name}' не найдена в структуре.")

    # Генерация клавиатуры
    keyboard = []

    # Добавляем кнопки для товаров в подкатегории
    for item in sub_structure[category_name]:
        keyboard.append([IB(text=item['text'], callback_data=item['callback'])])

    # Добавляем кнопку "Назад"
    keyboard.append([IB(text="⬅️ Назад", callback_data=back_button)])

    IKkeyboard = IKM(
        inline_keyboard=keyboard,
        row_width=2
    )

    return IKkeyboard

async def itemMenu(invoiceLink):
    IK = IKM(
        inline_keyboard=[
            [IB(text="Оплатить 🛒", url=invoiceLink)],
            [IB(text="⬅️ Назад", callback_data="backSub")],
        ],
        row_width=2
    )
    return IK
