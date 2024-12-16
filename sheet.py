import gspread
from oauth2client.service_account import ServiceAccountCredentials
from handlers import JsonDispatcher
from config import menu_structure
import logger
import time
# Настройка доступа через API Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(credentials)


# Настройка логирования
botLogger = logger.get_logger('bot')


def get_categories(sheet_name):
    """
    Получает все данные из Google Sheets и обновляет JSON-файл с категориями и ценами.
    Проверяет, что для каждого заголовка столбца есть хотя бы одно значение в столбце.

    :param sheet_name: Название таблицы Google Sheets
    :return: None
    """
    # Открываем таблицу и выбираем первый лист
    sheet = client.open(sheet_name)
    sell_sheet = sheet.get_worksheet(0)

    # Получаем все данные из таблицы
    data = sell_sheet.get_all_values()

    # Колонка F (индекс 5, так как индексация с 0)
    column_f = [row[5] for row in data[1:] if len(row) > 5 and row[5].strip() != ""]

    # Количество тарифов равно количеству заполненных значений в колонке F
    num_tariffs = len(column_f)

    # Данные из первой строки для количества тарифов
    header_data = [data[0][i] for i in range(num_tariffs) if data[0][i].strip() != ""]

    # Читаем существующие данные из JSON
    json_data = JsonDispatcher.read_data()

    # Обновляем sub_structure
    sub_structure = json_data.get("sub_structure", {})

    # Проверяем, что для каждого заголовка есть хотя бы одно ненулевое значение в столбце
    valid_header_data = []
    for i in range(len(header_data)):
        # Получаем данные для этого столбца
        column_data = [row[i] for row in data[1:] if len(row) > i]

        # Проверяем, что есть хотя бы одно значение, отличное от пустой строки
        if any(column_data):  # Если в столбце есть хотя бы одно ненулевое значение
            valid_header_data.append({"text": header_data[i], "callback": f"item_{i + 1}"})
        else:
            print(f"Столбец '{header_data[i]}' не содержит данных и будет пропущен.")

    # Обновляем sub_structure только с валидными данными
    sub_structure[sheet_name] = valid_header_data

    # Обновляем price_data
    price_data = json_data.get("price_data", {})

    # Получаем курс
    curs = sell_sheet.cell(2, 8).value  # Предположим, курс находится в ячейке H2
    price_data.update({header_data[i]: column_f[i] for i in range(len(valid_header_data)) if valid_header_data[i]})

    # Обновляем курс
    price_data.update({'curs': curs})

    # Сохраняем изменения в JSON
    json_data["sub_structure"] = sub_structure
    json_data["price_data"] = price_data
    JsonDispatcher.write_data(json_data)

def find_parent_and_callback(sub_structure, target_text):
    # Проходим по каждому родителю в структуре
    for parent, items in sub_structure.items():
        # Ищем в списке элементов
        for item in items:
            if item["text"] == target_text:
                # Если нашли совпадение, возвращаем родителя и callback
                return parent, item["callback"]
    return None  # Если не нашли

def get_order(name, userID):
    try:
        sub_structure = JsonDispatcher.get_sub_structure()
        result = find_parent_and_callback(sub_structure, name)

        if result:
            sheet, callback = result
            index = int(callback.split('item_')[1])
            # Теперь вызываем copy_and_append_data с обработкой ошибок
            token = copy_and_append_data(sheet_name=sheet, index=index, userID=userID, name=name)
            if token:
                botLogger.info(f"Товар {name} добавлен в заказ.")
                return token
            else:
                botLogger.warning(f"Не удалось добавить товар {name}.")
                return None
        else:
            botLogger.info(f"Не найдено соответствие для {name}, {userID}")
            return None
    except Exception as e:
        botLogger.error(f"Ошибка при обработке заказа {name}, {userID}: {e}")
        # Возможно, отправим уведомление пользователю (если это нужно)
        return None


def copy_and_append_data(sheet_name, index, userID, name):
    """
    Открывает таблицу Google Sheets, извлекает стоимость из указанного столбца
    (по индексу) и вставляет ее в другой лист, добавляя данные name и userID.

    :param sheet_name: Название таблицы Google Sheets
    :param index: Индекс столбца с токенами
    :param userID: ID пользователя
    :return: None
    """
    try:
        # Открываем таблицу и выбираем первый и второй лист
        sheet = client.open(sheet_name)
        first_sheet = sheet.get_worksheet(0)  # Получаем первый лист
        second_sheet = sheet.get_worksheet(1)  # Получаем второй лист

        # Получаем все данные с первого листа
        data = first_sheet.get_all_values()

        # Извлекаем токен из последней строки в указанном столбце
        token = None
        row_to_clear = None
        for i, row in reversed(list(enumerate(data))):  # Идем от конца к началу
            if row[index-1].strip():  # Проверяем, что значение не пустое
                token = row[index-1]
                row_to_clear = i + 1  # Запоминаем индекс строки (индексация с 1), где нужно очистить ячейку
                break  # Прерываем цикл, когда нашли первое непустое значение

        if token:
            if token == name:
                return None
            # Подготавливаем данные для вставки в новый лист
            new_row = [token, userID]

            # Вставляем данные в конец второго листа
            second_sheet.append_row(new_row)
            first_sheet.update_cell(row_to_clear, index, "")  # Устанавливаем ячейку пустой
            botLogger.info(f"Данные {new_row} успешно добавлены в второй лист.")
            return token
        else:
            botLogger.warning(f"Не удалось найти токен для {name} в листе.")
            return None
    except Exception as e:
        botLogger.error(f"Ошибка при копировании данных в Google Sheets: {e}")
        return None


def get_new_data():
    sheets = []
    # Получаем все таблицы, к которым есть доступ
    sheetsOpen = client.openall()

    # Выводим список названий таблиц
    sheet_titles = [sheet.title for sheet in sheetsOpen]

    firstCat = menu_structure.keys()
    for cat in firstCat:
        sub =  menu_structure[cat]
        for i in sub:
            sN = i.get('text')
            if sN in sheet_titles:
                print(sN)
            sheets.append(sN)

    for sheet in sheets:
        try:
            get_categories(sheet)
            time.sleep(3)
            botLogger.info(f"Обновили данные - {sheet}")
        except Exception as e:
            botLogger.error(f"Ошибка обновления данных - {sheet} - {e}")
