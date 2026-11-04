# Запуск на nurlight.moji.rest

Панель и бот работают на Mac Нурдаулета, а снаружи открываются через Cloudflare Tunnel
по адресу https://nurlight.moji.rest. Порты на роутере не открываются, HTTPS даёт Cloudflare.
Сайт доступен, пока Mac включён и запущен скрипт.

```
Клиент Telegram ──► серверы Telegram ◄── бот (polling) ─┐
                                                        ├─ prod.sqlite3
Оператор ──HTTPS──► Cloudflare ──туннель──► gunicorn ───┘   (панель Django)
```

## Однократная настройка

```bash
brew install cloudflared
cloudflared tunnel login                               # в браузере выбрать moji.rest
cloudflared tunnel create nurlight
cloudflared tunnel route dns nurlight nurlight.moji.rest
cp deploy/public.env.example deploy/public.env         # заполнить: ключ, BOT_TOKEN
```

Первый администратор боевой панели:

```bash
set -a; . deploy/public.env; set +a
.venv/bin/python admin_panel/manage.py migrate
.venv/bin/python admin_panel/manage.py createsuperuser
```

Операторов и руководителя заводит администратор в панели: «Пользователи» → добавить,
отметить «Статус персонала», выбрать группу «Оператор» или «Руководитель».

## Запуск

```bash
./deploy/start_public.sh
```

Скрипт применяет миграции, собирает статику и запускает три процесса: панель (gunicorn),
бота (если задан `BOT_TOKEN`) и туннель. Ctrl+C останавливает всё.

## Важно

- Боевая база `prod.sqlite3` отдельная от `db.sqlite3` для разработки. Команда `seed_demo`
  в боевом режиме не работает, чтобы в открытую панель не попали демо-пароли.
- Один токен бота нельзя запускать в двух местах одновременно: пока бот работает здесь,
  разработчик запускает у себя отдельного тестового бота со своим токеном.
- `deploy/public.env` содержит секреты и в git не попадает.
- Переезд на VPS: те же шаги на сервере; `TUNNEL_NAME` и DNS остаются прежними.
