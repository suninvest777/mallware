@echo off
chcp 65001 >nul
title Android App Test

cd /d "%~dp0"

echo ========================================
echo   Тестирование Android приложения
echo ========================================
echo.

python test_android_simulation.py

echo.
echo ========================================
pause
