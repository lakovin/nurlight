#!/bin/sh
# Режим соединения сайта с базой.
#   ./deploy/db_mode.sh on      — быстрый: соединение с базой держится открытым (перед показом)
#   ./deploy/db_mode.sh off     — обычный: новое соединение на каждый запрос, база Neon чаще засыпает
#   ./deploy/db_mode.sh status  — какой режим сейчас и как быстро отвечает сайт
# on/off меняют DB_PERSISTENT в deploy/public.env и перезапускают службу (~20 с без сайта).
set -eu
cd "$(dirname "$0")/.."
ENV_FILE=deploy/public.env
SERVICE="gui/$(id -u)/rest.moji.nurlight"
[ -f "$ENV_FILE" ] || { echo "нет $ENV_FILE"; exit 1; }

current() {
    if grep -q '^DB_PERSISTENT=1' "$ENV_FILE"; then echo on; else echo off; fi
}

site_url() {
    host=$(grep '^DJANGO_ALLOWED_HOSTS=' "$ENV_FILE" | cut -d= -f2 | cut -d, -f1 | tr -d "'\"")
    echo "https://$host/"
}

measure() {
    url=$(site_url)
    for i in 1 2 3; do
        curl -s -o /dev/null -m 20 -w "  ответ %{http_code} за %{time_total} с\n" "$url" || echo "  нет ответа"
    done
}

set_mode() {
    value=$1
    if grep -q '^DB_PERSISTENT=' "$ENV_FILE"; then
        sed -i '' "s/^DB_PERSISTENT=.*/DB_PERSISTENT=$value/" "$ENV_FILE"
    else
        printf '\nDB_PERSISTENT=%s\n' "$value" >> "$ENV_FILE"
    fi
    if launchctl print "$SERVICE" >/dev/null 2>&1; then
        launchctl kickstart -k "$SERVICE"
        printf 'служба перезапущена, жду сайт'
        url=$(site_url)
        for i in $(seq 1 24); do
            sleep 5
            [ "$(curl -s -o /dev/null -m 10 -w '%{http_code}' "$url")" = 200 ] && { echo " — готово"; return; }
            printf '.'
        done
        echo " — сайт не ответил за 2 минуты, смотрите ~/Library/Logs/nurlight.log"
    else
        echo "автозапуск не установлен — перезапустите ./deploy/start_public.sh вручную"
    fi
}

case "${1:-status}" in
    on)  set_mode 1; echo "режим: быстрый (постоянное соединение)"; measure ;;
    off) set_mode 0; echo "режим: обычный (соединение на каждый запрос)"; measure ;;
    status) echo "режим: $(current)"; measure ;;
    *) echo "использование: $0 on|off|status"; exit 1 ;;
esac
