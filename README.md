# Nurlight Delivery Bot

Дипломный проект команды Nurlight: Telegram-бот, через который клиенты службы доставки
оформляют и отслеживают заказы, и веб-панель на Django, где операторы их обрабатывают.

Бот (aiogram 3) и панель (Django) работают с одной базой данных. Таблицы описаны
моделями Django в `admin_panel/delivery/models.py`, а бот использует эти же модели через ORM.

## Команда

| Участник | Роль |
|---|---|
| Ислам | Аналитик: предметная область, требования, сценарии диалогов (глава 1) |
| Нурадыл | Разработчик бота: оформление заказа, статусы, FAQ (глава 2) |
| Нурдаулет | Админ-панель, тестирование, экономика (глава 3) |

## Структура

```
bot/                  # Telegram-бот (aiogram 3)
├── main.py           # точка входа
├── handlers/         # обработчики: /start, каталог
├── keyboards/        # кнопки
├── states.py         # FSM-состояния оформления заказа
└── services/         # работа с базой
admin_panel/          # Django-проект
├── manage.py
├── config/           # settings, urls
└── delivery/         # модели, admin.py, демо-данные
docs/                 # схемы, требования, сценарии диалогов
```

## Запуск

Нужен Python 3.11+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # вписать BOT_TOKEN от @BotFather
```

Для разработки проще всего SQLite — в `.env` укажите `DATABASE_URL=sqlite:///db.sqlite3`.
Для PostgreSQL — строку вида `postgres://user:password@localhost:5432/nurlight`.

Создать таблицы, загрузить демо-каталог и завести администратора:

```bash
cd admin_panel
python manage.py migrate
python manage.py loaddata demo_catalog
python manage.py createsuperuser
```

Панель (http://127.0.0.1:8000/admin/):

```bash
cd admin_panel
python manage.py runserver
```

Бот (из корня репозитория):

```bash
python -m bot.main
```

## Статусы заказа

новый → принят → передан курьеру → в пути → доставлен; отдельно «отменён».

## Что уже есть

- модели: Client, Category, Product, Order, OrderItem, Courier, FAQ;
- панель: заказы с фильтрами, сменой статуса и курьера прямо в списке;
- бот: `/start` (регистрирует клиента) и каталог по категориям.

## Дальше

- корзина и оформление заказа (FSM в `bot/states.py`);
- уведомления клиенту при смене статуса;
- FAQ и связь с оператором;
- роли «оператор» и «руководитель», страница статистики.
