import re

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery


class IsDigit(BaseFilter):
    async def __call__(self, message) -> bool:
        # Регулярное выражение для проверки целых и дробных чисел
        number_pattern = re.compile(r'^\d+([.,]\d+)?$')

        if isinstance(message, CallbackQuery):
            message = message.message
        if message.text:
            if number_pattern.match(message.text):
                return True
        return False


class IsText(BaseFilter):
    async def __call__(self, message) -> bool:
        if isinstance(message, CallbackQuery):
            message = message.message
        if message.text:
            return True
        return False


class TextFilter(BaseFilter):
    def __init__(self, pattern: str):
        self.pattern = re.compile(pattern)

    async def __call__(self, message) -> bool:
        if isinstance(message, CallbackQuery):
            message = message.message
        if message.text and self.pattern.match(message.text):
            return True
        return False
