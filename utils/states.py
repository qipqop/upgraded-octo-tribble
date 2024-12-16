from aiogram.fsm.state import State, StatesGroup


class UserStatus(StatesGroup):
    """"
    usual - Состояние пользователя не в процессе\n
    """
    usual = State()
