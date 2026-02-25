"""
Утилита для встраивания exe файла в JPEG изображение (стеганография)
Метод: добавление данных после маркера конца JPEG (0xFFD9)
"""
import sys
import os


def embed_exe_in_image(image_path, exe_path, output_path):
    """
    Встраивает exe файл в JPEG изображение.
    
    Args:
        image_path (str): Путь к исходному JPEG изображению
        exe_path (str): Путь к exe файлу для встраивания
        output_path (str): Путь для сохранения результата
    
    Returns:
        bool: True если успешно, False в противном случае
    """
    try:
        # Читаем изображение
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Проверяем, что это JPEG
        if not image_data.startswith(b'\xff\xd8'):
            print("Ошибка: файл не является валидным JPEG", file=sys.stderr)
            return False
        
        # Находим маркер конца JPEG (0xFFD9)
        end_marker = b'\xff\xd9'
        last_marker_pos = image_data.rfind(end_marker)
        
        if last_marker_pos == -1:
            print("Ошибка: не найден маркер конца JPEG", file=sys.stderr)
            return False
        
        # Читаем exe файл
        with open(exe_path, 'rb') as f:
            exe_data = f.read()
        
        # Создаем маркер начала встроенных данных (для идентификации)
        embed_marker = b'\xff\xd8\xff\xe0'  # Похож на JPEG заголовок, но это наш маркер
        embed_size = len(exe_data).to_bytes(4, 'little')  # Размер exe в 4 байтах
        
        # Собираем финальный файл:
        # 1. JPEG данные до маркера конца
        # 2. Маркер конца JPEG (0xFFD9)
        # 3. Наш маркер встроенных данных
        # 4. Размер exe
        # 5. Данные exe
        result = (
            image_data[:last_marker_pos + 2] +  # JPEG до конца включительно
            embed_marker +                       # Наш маркер
            embed_size +                         # Размер exe
            exe_data                            # Сам exe
        )
        
        # Сохраняем результат
        with open(output_path, 'wb') as f:
            f.write(result)
        
        print(f"Успешно! Exe файл встроен в изображение.")
        print(f"Исходное изображение: {len(image_data)} байт")
        print(f"Exe файл: {len(exe_data)} байт")
        print(f"Результат: {len(result)} байт")
        print(f"Сохранено в: {output_path}")
        
        return True
        
    except FileNotFoundError as e:
        print(f"Ошибка: файл не найден - {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return False


def extract_exe_from_image(image_path, output_exe_path):
    """
    Извлекает exe файл из изображения.
    
    Args:
        image_path (str): Путь к изображению с встроенным exe
        output_exe_path (str): Путь для сохранения извлеченного exe
    
    Returns:
        bool: True если успешно, False в противном случае
    """
    try:
        # Читаем файл
        with open(image_path, 'rb') as f:
            data = f.read()
        
        # Ищем маркер конца JPEG
        end_marker = b'\xff\xd9'
        last_marker_pos = data.rfind(end_marker)
        
        if last_marker_pos == -1:
            print("Ошибка: не найден маркер конца JPEG", file=sys.stderr)
            return False
        
        # Ищем наш маркер встроенных данных
        embed_marker = b'\xff\xd8\xff\xe0'
        embed_pos = data.find(embed_marker, last_marker_pos)
        
        if embed_pos == -1:
            print("Ошибка: не найден маркер встроенных данных", file=sys.stderr)
            return False
        
        # Читаем размер exe (4 байта после маркера)
        size_pos = embed_pos + len(embed_marker)
        if size_pos + 4 > len(data):
            print("Ошибка: недостаточно данных для чтения размера", file=sys.stderr)
            return False
        
        exe_size = int.from_bytes(data[size_pos:size_pos + 4], 'little')
        
        # Читаем exe данные
        exe_start = size_pos + 4
        exe_end = exe_start + exe_size
        
        if exe_end > len(data):
            print("Ошибка: недостаточно данных для извлечения exe", file=sys.stderr)
            return False
        
        exe_data = data[exe_start:exe_end]
        
        # Сохраняем exe
        with open(output_exe_path, 'wb') as f:
            f.write(exe_data)
        
        print(f"Успешно! Exe файл извлечен: {len(exe_data)} байт")
        print(f"Сохранено в: {output_exe_path}")
        
        return True
        
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return False


def main():
    """Основная функция"""
    if len(sys.argv) < 2:
        print("Использование:")
        print("  Встраивание: embed_exe_in_image.py embed <image.jpg> <file.exe> <output.jpg>")
        print("  Извлечение:  embed_exe_in_image.py extract <image.jpg> <output.exe>")
        return 1
    
    command = sys.argv[1].lower()
    
    if command == 'embed':
        if len(sys.argv) != 5:
            print("Ошибка: неверное количество аргументов", file=sys.stderr)
            print("Использование: embed_exe_in_image.py embed <image.jpg> <file.exe> <output.jpg>")
            return 1
        
        image_path = sys.argv[2]
        exe_path = sys.argv[3]
        output_path = sys.argv[4]
        
        if embed_exe_in_image(image_path, exe_path, output_path):
            return 0
        else:
            return 1
    
    elif command == 'extract':
        if len(sys.argv) != 4:
            print("Ошибка: неверное количество аргументов", file=sys.stderr)
            print("Использование: embed_exe_in_image.py extract <image.jpg> <output.exe>")
            return 1
        
        image_path = sys.argv[2]
        output_exe_path = sys.argv[3]
        
        if extract_exe_from_image(image_path, output_exe_path):
            return 0
        else:
            return 1
    
    else:
        print(f"Ошибка: неизвестная команда '{command}'", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
