# PhotoView - Простое приложение для просмотра фото

Простое Android приложение для просмотра фотографий.

## Автоматическая сборка

Этот репозиторий поддерживает несколько способов сборки Android APK:

### Вариант 1: Google Colab (Рекомендуется для начинающих)

Самый простой способ - использовать Google Colab без локальной установки:

1. Откройте файл [`build_android_colab.ipynb`](build_android_colab.ipynb) в [Google Colab](https://colab.research.google.com/)
2. Запустите все ячейки (Runtime → Run all)
3. Дождитесь завершения сборки (30-60 минут при первой сборке)
4. Скачайте APK из последней ячейки

**Подробная инструкция:** См. [COLAB_GUIDE.md](COLAB_GUIDE.md)

### Вариант 2: GitHub Actions

Автоматическая сборка при каждом push:

1. Перейдите в раздел [Actions](https://github.com/suninvest777/mallware/actions)
2. Дождитесь завершения сборки (10-20 минут)
3. Скачайте APK из раздела Artifacts

### Вариант 3: Локальная сборка (WSL/Linux)

Для локальной сборки на Windows используйте WSL, на Linux/Mac - напрямую:

```bash
# Установка зависимостей
sudo apt install -y python3-pip python3-dev git unzip openjdk-17-jdk
pip3 install --user buildozer cython

# Сборка APK
cd ready_app
buildozer android debug
```

APK будет в папке `ready_app/bin/`

### Установка

1. Скачайте APK файл
2. Установите на Android устройство
3. Откройте приложение
4. Наслаждайтесь просмотром фото

## Технические детали

- Python 3.10
- Buildozer для сборки
- Kivy для интерфейса (опционально)

## Лицензия

MIT
