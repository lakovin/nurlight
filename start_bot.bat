@echo off
rem Запуск бота двойным щелчком. Если бот упал (например, пропал интернет),
rem он перезапустится через 10 секунд. Остановить: закрыть это окно.
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"
title Nurlight bot

if not exist venv\Scripts\python.exe (
    echo Нет папки venv. Выполните: python -m venv venv
    echo затем: venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)
if not exist .env (
    echo Нет файла .env. Скопируйте .env.example в .env и заполните.
    pause
    exit /b 1
)

:loop
echo [%date% %time%] Запуск бота...
venv\Scripts\python.exe -m bot.main
echo [%date% %time%] Бот остановился. Перезапуск через 10 секунд...
ping -n 11 127.0.0.1 >nul
goto loop
