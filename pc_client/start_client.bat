@echo off
chcp 65001 >nul
title Android Remote Control Client

echo ========================================
echo   Android Remote Control Client
echo ========================================
echo.

cd /d "%~dp0"

echo Проверка зависимостей...
python -c "import tkinter" 2>nul
if errorlevel 1 (
    echo [ОШИБКА] tkinter не найден. Установите Python с tkinter.
    pause
    exit /b 1
)

python -c "import PIL" 2>nul
if errorlevel 1 (
    echo Установка Pillow...
    pip install -q Pillow numpy
)

echo.
echo Запуск клиента...
echo.
python pc_client.py

if errorlevel 1 (
    echo.
    echo [ОШИБКА] Не удалось запустить клиент.
    pause
)
