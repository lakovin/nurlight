from aiogram.fsm.state import State, StatesGroup


class OrderForm(StatesGroup):
    """Шаги оформления заказа: геолокация → уточнение адреса → телефон → комментарий → подтверждение."""

    location = State()
    address = State()  # необязательное уточнение: подъезд, этаж, квартира
    phone = State()
    comment = State()
    confirm = State()
