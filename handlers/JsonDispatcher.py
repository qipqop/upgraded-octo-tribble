import json

# Путь к JSON-файлу
DATA_FILE = "handlers/marketData.json"


def read_data():
    """
    Читает данные из JSON-файла.
    :return: Словарь с данными.
    """
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"sub_structure": {}, "price_data": {}}
    except json.JSONDecodeError as e:
        raise ValueError(f"Ошибка чтения JSON-файла: {e}")

def write_data(data):
    """
    Записывает данные в JSON-файл.
    :param data: Словарь с данными.
    """
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def get_sub_structure():
    """
    Получает структуру подкатегорий.
    :return: Словарь с подкатегориями.
    """
    data = read_data()
    return data.get("sub_structure", {})

def get_price_data():
    """
    Получает данные о ценах.
    :return: Словарь с ценами.
    """
    data = read_data()
    return data.get("price_data", {})

def update_sub_structure(sub_structure):
    """
    Обновляет структуру подкатегорий.
    :param sub_structure: Новый словарь с подкатегориями.
    """
    data = read_data()
    data["sub_structure"] = sub_structure
    write_data(data)

def update_price_data(price_data):
    """
    Обновляет данные о ценах.
    :param price_data: Новый словарь с ценами.
    """
    data = read_data()
    data["price_data"] = price_data
    write_data(data)
