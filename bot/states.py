from aiogram.fsm.state import State, StatesGroup


class OrderForm(StatesGroup):
    """Шаги оформления заказа. Обработчики появятся вместе с корзиной."""

    address = State()
    phone = State()
    comment = State()
    confirm = State()
