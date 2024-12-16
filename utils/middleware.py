import logger
from aiogram.types import Message, TelegramObject, CallbackQuery
from aiogram import BaseMiddleware
from typing import Any, Awaitable, Callable, Dict

messageLogger = logger.get_logger('messages')


class MessageLogging(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message):
            userTgID = event.from_user.id
            messageText = event.text
            event_router = data.get('event_router', 'UnknownEventRouter')

            if messageText:  # Не проверяем на None, так как это излишне для строк
                messageLogger.info(
                    f"{event_router} - {userTgID} - {messageText}")

        return await handler(event, data)


class CallbackLogging(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, CallbackQuery):
            userTgID = event.message.chat.id
            callbackData = event.data
            event_router = data.get('event_router', 'UnknownEventRouter')

            messageLogger.info(f"{event_router} - {userTgID} - {callbackData}")

        return await handler(event, data)
