# Бот: как устроено и что делать дальше

Памятка для Нурадыла (разработка бота).

## 1. Обновиться и запустить

В GitHub Desktop: **Fetch origin**, затем **Pull origin**. Твой `bot/main.py` изменился:
бот разбит на папки по структуре из ТЗ, `/start` и каталог уже работают.

В терминале VS Code, из корня репозитория:

```bash
python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # macOS
pip install -r requirements.txt
```

В `.env` в корне репозитория (рядом с README) должны быть строки:

```
BOT_TOKEN=твой_токен
DATABASE_URL=sqlite:///db.sqlite3
```

Создать базу и заполнить демо-данными (один раз):

```bash
cd admin_panel
python manage.py migrate
python manage.py seed_demo
cd ..
```

Запуск бота — **из корня репозитория**, иначе не найдутся импорты:

```bash
python -m bot.main
```

Панель, чтобы видеть заказы из бота: `cd admin_panel && python manage.py runserver`,
затем http://127.0.0.1:8000/admin/ (логин `manager`, пароль `nurlight-demo`).

## 2. Как устроен бот

```
bot/
├── main.py          # запуск, подключение роутеров
├── handlers/        # один файл — один раздел: start.py, catalog.py, дальше cart.py, order.py, faq.py
├── keyboards/       # кнопки; callback-данные через CallbackData
├── states.py        # FSM оформления заказа (заготовка)
└── services/        # всё, что работает с базой
```

**Таблицы бот не описывает.** Модели лежат в `admin_panel/delivery/models.py`, бот подключает
их через `bot/services/db.py`. Поэтому:

- в обработчиках работаем с базой только через функции из `bot/services/`;
- используем асинхронные методы ORM: `aget`, `acreate`, `afirst`, `acount`, `async for`;
- если нужно поле, которого нет, — не создаём свою таблицу, а договариваемся и меняем модель,
  потом `python manage.py makemigrations` и `migrate`.

Пример запроса из `bot/services/catalog.py`:

```python
async def list_products(category_id: int) -> list[Product]:
    return [p async for p in Product.objects.filter(category_id=category_id, is_available=True)]
```

## 3. Что делать дальше (по порядку)

### Корзина
- Хранить корзину в FSM-данных пользователя: `await state.update_data(cart={product_id: qty})`.
  В таблицу не пишем, пока заказ не подтверждён.
- В карточке товара (`show_product` в `handlers/catalog.py`) добавить кнопки «➕ В корзину» / «➖».
- Кнопка «🛒 Корзина» в главном меню (`keyboards/main_menu.py`): список, сумма, «Оформить», «Очистить».

### Оформление заказа
Шаги уже описаны в `bot/states.py`: адрес → телефон → комментарий → подтверждение.
- Телефон удобнее брать кнопкой `KeyboardButton(text="📱 Отправить номер", request_contact=True)`
  и сохранять в `Client.phone`, чтобы не спрашивать второй раз.
- При подтверждении создаём заказ одной функцией в `bot/services/orders.py`. ORM-транзакции
  синхронные, поэтому оборачиваем в `sync_to_async`:

```python
from asgiref.sync import sync_to_async
from django.db import transaction

from delivery.models import Client, Order, OrderItem, Product


@sync_to_async
def create_order(telegram_id: int, cart: dict[int, int], address: str, comment: str) -> Order:
    with transaction.atomic():
        client = Client.objects.get(telegram_id=telegram_id)
        order = Order.objects.create(client=client, address=address, comment=comment)
        for product in Product.objects.filter(pk__in=cart, is_available=True):
            OrderItem.objects.create(order=order, product=product, quantity=cart[product.pk], price=product.price)
        order.recalculate_total()
    return order
```

- Цену записываем в `OrderItem.price` на момент заказа — если потом поменяют цену товара,
  старые заказы не изменятся. Сумму считает `order.recalculate_total()`.
- После создания показать клиенту «Заказ №{order.number} принят» — заказ сразу появится в панели
  со статусом «Новый».

### Мои заказы и статус
- «📦 Мои заказы»: последние 5 заказов клиента — `Order.objects.filter(client__telegram_id=...)[:5]`,
  статус выводить через `order.get_status_display()`.

### Уведомления о смене статуса
Статус меняет оператор в панели, а сообщение клиенту должен отправить бот. Это ещё не решено —
обсудим на созвоне. Варианты:
1. **Бот проверяет базу раз в 10–15 секунд** (фоновая задача в `main.py`): ищет заказы, у которых
   `updated_at` новее последней проверки, и пишет клиентам. Просто, вся логика в боте.
2. **Панель сама шлёт сообщение** через Telegram Bot API при сохранении заказа. Быстрее,
   но логика уведомлений окажется в панели.

Для первого варианта понадобится поле «какой статус клиенту уже сообщили» в `Order` — скажи,
добавлю в модель.

### FAQ и связь с оператором
- Вопросы уже есть в таблице `FAQ` (заполняются в панели). Кнопка «❓ Помощь» → список вопросов
  кнопками → ответ.
- «Связаться с оператором»: переслать сообщение клиента в чат операторов. ID чата вынести в `.env`
  (например, `OPERATORS_CHAT_ID`).

## 4. Правила работы с репозиторием

- Перед началом работы — **Pull**, перед пушем — проверить, что бот запускается.
- Один коммит — одна законченная вещь: «Корзина», «Оформление заказа», а не «правки».
- `.env` и `db.sqlite3` в git не попадают (они в `.gitignore`), токен никому не отправляем.
- Модели (`admin_panel/delivery/models.py`) меняем только после того, как договорились,
  и вместе с миграцией.
