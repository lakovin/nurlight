#!/bin/sh
# Запуск бота на macOS/Linux: sh start_bot.sh. Если бот упал, он перезапустится
# через 10 секунд. Остановить: Ctrl+C.
cd "$(dirname "$0")" || exit 1
PYTHON=venv/bin/python
[ -x "$PYTHON" ] || PYTHON=.venv/bin/python
[ -x "$PYTHON" ] || { echo "Нет venv: python3 -m venv venv && venv/bin/pip install -r requirements.txt"; exit 1; }
[ -f .env ] || { echo "Нет файла .env: скопируйте .env.example и заполните"; exit 1; }
trap 'exit 0' INT TERM
while true; do
    "$PYTHON" -m bot.main
    echo "Бот остановился. Перезапуск через 10 секунд..."
    sleep 10
done
