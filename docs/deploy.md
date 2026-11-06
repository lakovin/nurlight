# Запуск на nurlight.moji.rest

Панель и бот работают на Mac Нурдаулета, а снаружи открываются через Cloudflare Tunnel
по адресу https://nurlight.moji.rest. Порты на роутере не открываются, HTTPS даёт Cloudflare.
Сайт поднимается сам при входе в macOS и перезапускается при падении; недоступен, только пока
Mac выключен или спит.

Боевая копия живёт отдельно от рабочей: `~/nurlight-server` — клон репозитория с GitHub,
в нём `deploy/public.env`. Папка `~/Documents` не подходит: macOS не пускает
туда фоновые службы. Разработка по-прежнему идёт в своей папке.

```
Клиент Telegram ──► серверы Telegram ◄── бот (у Нурадыла) ──┐
                                                             ├─ PostgreSQL в Neon
Оператор ──HTTPS──► Cloudflare ──туннель──► gunicorn ────────┘   (проект nurlight, Франкфурт)
```

База — облачный PostgreSQL в Neon, общий для панели и бота: строка подключения стоит в
`DATABASE_URL` в `deploy/public.env` (в кавычках — в ней есть `&`). Резервная копия прежней
SQLite-базы — `~/nurlight-server/backups/`.

## Однократная настройка

```bash
git clone https://github.com/lakovin/nurlight.git ~/nurlight-server
cd ~/nurlight-server
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
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

Автозапуск (один раз, из `~/nurlight-server`):

```bash
./deploy/install_autostart.sh            # включить
./deploy/install_autostart.sh --remove   # выключить
```

Служба запускает `deploy/start_public.sh`: миграции, сборка статики, затем панель (gunicorn),
бот (если задан `BOT_TOKEN`) и туннель. Лог — `~/Library/Logs/nurlight.log`.

Обновить сайт после новых коммитов:

```bash
cd ~/nurlight-server && git pull && .venv/bin/pip install -r requirements.txt
launchctl kickstart -k gui/$(id -u)/rest.moji.nurlight
```

Вручную, без автозапуска: `./deploy/start_public.sh`, Ctrl+C останавливает всё.

## Важно

- Боевая база (Neon) отдельная от `db.sqlite3` для разработки. Команда `seed_demo`
  в боевом режиме не работает, чтобы в открытую панель не попали демо-пароли.
- Резервная копия боевой базы: `set -a; . deploy/public.env; set +a`, затем
  `.venv/bin/python admin_panel/manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.permission -e sessions -o backups/<дата>.json`.
- Один токен бота нельзя запускать в двух местах одновременно. Основной бот работает у Нурадыла,
  поэтому `BOT_TOKEN` в `deploy/public.env` здесь пустой.
- `deploy/public.env` содержит секреты и в git не попадает.
- Переезд на VPS: те же шаги на сервере; `TUNNEL_NAME` и DNS остаются прежними.
