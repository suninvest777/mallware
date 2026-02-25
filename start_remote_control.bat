@echo off
chcp 65001 >nul
title Android Remote Control - Запуск клиента

cd /d "%~dp0"

if not exist "pc_client\pc_client.py" (
    echo [ОШИБКА] Файл pc_client\pc_client.py не найден!
    pause
    exit /b 1
)

cd pc_client
call start_client.bat
