import aiosqlite
import json
from aiogram.fsm.storage.base import BaseStorage, StorageKey
from typing import Dict, Any, Optional
from aiogram.fsm.state import State
import asyncio


class SQLiteStorage(BaseStorage):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.initialized = False
        asyncio.run(self.initialize())

    async def initialize(self):
        if not self.initialized:
            # Создаем таблицу в базе данных, если она не существует
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS fsm_storage (
                        bot_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        chat_id INTEGER NOT NULL,
                        state TEXT,
                        data TEXT,
                        PRIMARY KEY (bot_id, user_id, chat_id)
                    );
                ''')
                await db.commit()
            self.initialized = True

    async def create_pool(self):
        # В SQLite pool не используется, так что этот метод не нужен
        pass

    async def close(self):
        # Также не требуется, так как соединение закрывается после каждого запроса
        pass

    async def set_state(self, key: StorageKey, state: Optional[State] = None):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO fsm_storage(bot_id, user_id, chat_id, state) VALUES(?, ?, ?, ?) "
                "ON CONFLICT(bot_id, user_id, chat_id) DO UPDATE SET state = ?;",
                (key.bot_id, key.user_id, key.chat_id, state.state if state else None, state.state if state else None))
            await db.commit()

    async def get_state(self, key: StorageKey) -> Optional[str]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT state FROM fsm_storage WHERE bot_id = ? AND user_id = ? AND chat_id = ?;",
                (key.bot_id, key.user_id, key.chat_id))
            row = await cursor.fetchone()
            return row[0] if row else None

    async def set_data(self, key: StorageKey, data: Dict[str, Any]):
        serialized_data = json.dumps(data)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO fsm_storage(bot_id, user_id, chat_id, data) VALUES(?, ?, ?, ?) "
                "ON CONFLICT(bot_id, user_id, chat_id) DO UPDATE SET data = ?;",
                (key.bot_id, key.user_id, key.chat_id, serialized_data, serialized_data))
            await db.commit()

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT data FROM fsm_storage WHERE bot_id = ? AND user_id = ? AND chat_id = ?;",
                (key.bot_id, key.user_id, key.chat_id))
            row = await cursor.fetchone()
            if row and row[0]:
                return json.loads(row[0])
            else:
                return {}

    async def update_data(self, key: StorageKey, data: Dict[str, Any]) -> Dict[str, Any]:
        current_data = await self.get_data(key)
        current_data.update(data)
        await self.set_data(key, current_data)
        return current_data

    async def get_user_count(self) -> int:
        """
        Возвращает количество уникальных пользователей в базе данных.
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(DISTINCT user_id) FROM fsm_storage")
            (count,) = await cursor.fetchone()
            return count

    async def get_all_user_ids(self) -> list:
        """
        Возвращает список уникальных Telegram ID всех пользователей.
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT DISTINCT user_id FROM fsm_storage")
            users = await cursor.fetchall()
            return [user[0] for user in users]
