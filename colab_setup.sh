#!/bin/bash
# Скрипт для автоматической установки всех зависимостей в Google Colab
# Используется как вспомогательный скрипт для build_android_colab.ipynb

set -e  # Остановка при ошибке

echo "=========================================="
echo "Установка зависимостей для сборки Android APK"
echo "=========================================="
echo ""

# Обновляем систему
echo "[1/5] Обновление системы..."
apt-get update -qq

# Устанавливаем системные зависимости
echo "[2/5] Установка системных зависимостей..."
apt-get install -y -qq \
    openjdk-17-jdk \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    libtool \
    automake \
    autoconf \
    libltdl-dev \
    pkg-config \
    m4 \
    git \
    unzip \
    wget

echo "✓ Системные зависимости установлены"

# Устанавливаем Python зависимости
echo "[3/5] Установка Python зависимостей..."
pip3 install --quiet --user buildozer cython>=0.29.21

# Добавляем в PATH
export PATH="$HOME/.local/bin:$PATH"

echo "✓ Python зависимости установлены"
echo "✓ Buildozer версия:"
buildozer --version

# Настраиваем Android SDK лицензии
echo "[4/5] Настройка Android SDK лицензий..."
SDK_PATH="$HOME/.buildozer/android/platform/android-sdk"
mkdir -p "$SDK_PATH/licenses"

# Принимаем все лицензии автоматически
echo "24333f8a63b6825ea9c5514f83c2829b004d1fee" > "$SDK_PATH/licenses/android-sdk-license"
echo "84831b9409646a918e30573bab4c9c91346d8abd" > "$SDK_PATH/licenses/android-sdk-preview-license"
echo "8403addf88ab4874007e1c1e80a0025de2550a16" > "$SDK_PATH/licenses/android-googletv-license"
echo "601085b94cd77f0b54ff86406957099ebe79c4d6" > "$SDK_PATH/licenses/android-sdk-arm-dbt-license"
echo "33b6a2b64607f11b759f320ef9dff4ae5c47d97a" > "$SDK_PATH/licenses/google-gdk-license"
echo "d975f751698a77b662f1254ddbeed3901e976f5a" > "$SDK_PATH/licenses/intel-android-extra-license"
echo "e9acab5e5f1efb7a6c54c6850d6c4c78afd05907" > "$SDK_PATH/licenses/mips-android-sysimage-license"

echo "✓ Лицензии Android SDK приняты"

# Проверяем установку
echo "[5/5] Проверка установки..."
echo ""
echo "Проверка компонентов:"
echo -n "  Java: "
java -version 2>&1 | head -1 || echo "не найден"

echo -n "  Git: "
git --version || echo "не найден"

echo -n "  Buildozer: "
buildozer --version || echo "не найден"

echo -n "  Cython: "
python3 -c "import cython; print(cython.__version__)" 2>/dev/null || echo "не найден"

echo ""
echo "=========================================="
echo "✓ Установка завершена!"
echo "=========================================="
echo ""
echo "Следующие шаги:"
echo "1. Загрузите проект (клонирование или загрузка файлов)"
echo "2. Перейдите в директорию ready_app/"
echo "3. Запустите: buildozer android debug"
echo ""
