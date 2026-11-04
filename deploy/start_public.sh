#!/bin/sh
# Запускает панель, бота и туннель Cloudflare. Остановить: Ctrl+C.
set -e
cd "$(dirname "$0")/.."

if [ ! -f deploy/public.env ]; then
    echo "Нет deploy/public.env — скопируйте deploy/public.env.example и заполните"
    exit 1
fi
set -a
. deploy/public.env
set +a

PYTHON=.venv/bin/python
"$PYTHON" admin_panel/manage.py migrate --noinput
"$PYTHON" admin_panel/manage.py collectstatic --noinput -v0

trap 'kill 0' INT TERM EXIT

.venv/bin/gunicorn --chdir admin_panel config.wsgi \
    --bind "127.0.0.1:$PANEL_PORT" --workers 2 --access-logfile - &

if [ -n "$BOT_TOKEN" ]; then
    "$PYTHON" -m bot.main &
else
    echo "BOT_TOKEN пуст — бот не запущен, работает только панель"
fi

cloudflared tunnel --no-autoupdate run --url "http://127.0.0.1:$PANEL_PORT" "$TUNNEL_NAME" &

echo "Панель: https://nurlight.moji.rest"
wait
