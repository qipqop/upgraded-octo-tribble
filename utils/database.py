import aiosqlite
import asyncio
import logger

botLogger = logger.get_logger('bot')


class AsyncDatabaseManager:
    def __init__(self, db_file):
        self.db_file = db_file
        asyncio.run(self.initialize_database())
        self.dbUsers = UsersDB(self.db_file)

    async def initialize_database(self):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dateOfCreation TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    dateOfUpdate TEXT,
                    userTgID INTEGER,
                    userChatID INTEGER,
                    userTgUsername TEXT
                );
            """)

class UsersDB:
    def __init__(self, db_file):
        self.db_file = db_file

    async def add_user(self, user_data):
        """add_user(self, user_data): Добавляет нового пользователя в базу данных.
        Параметры:
        user_data (dict): Словарь с данными пользователя, который должен содержать:
        userTgID (int): Telegram ID пользователя
        userChatID (int): Chat ID пользователя
        userTgUsername (str): Имя пользователя в Telegram
        Возвращает: str - 'exist' если пользователь с таким userTgID уже существует, иначе 'added'
        """
        async with aiosqlite.connect(self.db_file) as db:
            exists = await db.execute("SELECT 1 FROM users WHERE userTgID = ?", (user_data['userTgID'],))
            exists = await exists.fetchone()
            if exists:
                return 'exist'
            await db.execute("""
                INSERT INTO users (dateOfCreation, dateOfUpdate, userTgID, userChatID, userTgUsername)
                VALUES (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?, ?, ?);
            """, (user_data['userTgID'], user_data['userChatID'], user_data['userTgUsername']))
            await db.commit()
            return 'added'

    async def update_user(self, user_tg_id, updated_data):
        """update_user(self, user_tg_id, updated_data): Обновляет данные существующего пользователя в базе данных по его Telegram ID. Параметры:
            user_tg_id (int): Telegram ID пользователя, данные которого нужно обновить
            updated_data (dict): Словарь с обновляемыми данными, например:
            userChatID: новый Chat ID
            userTgUsername: новое имя пользователя
            Возвращает: str - 'updated' после успешного обновления данных
        """
        async with aiosqlite.connect(self.db_file) as db:
            columns = ", ".join([f"{key} = ?" for key in updated_data])
            values = list(updated_data.values())
            values.append(user_tg_id)
            await db.execute(f"UPDATE users SET {columns} WHERE userTgID = ?", values)
            await db.commit()
            return 'updated'

    async def get_user_by_tgid(self, user_tg_id):
        """get_user_by_tgid(self, user_tg_id): Получает данные пользователя по его Telegram ID. Параметры:
            user_tg_id (int): Telegram ID пользователя
            Возвращает: dict - данные пользователя или 'no user found' если пользователь не найден
        """
        async with aiosqlite.connect(self.db_file) as db:
            cursor = await db.execute("SELECT * FROM users WHERE userTgID = ?", (user_tg_id,))
            user = await cursor.fetchone()
            return user if user else None

    async def get_all_users(self):
        """get_all_users(self): Получает всех пользователей из базы данных.
            Возвращает: list - список пользователей
        """
        async with aiosqlite.connect(self.db_file) as db:
            cursor = await db.execute("SELECT * FROM users")
            users = await cursor.fetchall()
            return users if users else []
