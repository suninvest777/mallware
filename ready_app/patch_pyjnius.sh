#!/bin/bash
# Патч для исправления long -> int в pyjnius для совместимости с Python 3
# Этот скрипт заменяет устаревший синтаксис Python 2 (long) на Python 3 (int)

echo "=== Применение патча для pyjnius ==="

# Ищем файл jnius_utils.pxi в установленном pyjnius
PYJNIUS_PATH=$(find .buildozer -path "*/pyjnius/jnius/jnius_utils.pxi" 2>/dev/null | head -1)

if [ -z "$PYJNIUS_PATH" ]; then
  # Пробуем найти в других местах
  PYJNIUS_PATH=$(find $HOME/.buildozer -path "*/pyjnius/jnius/jnius_utils.pxi" 2>/dev/null | head -1)
fi

if [ -n "$PYJNIUS_PATH" ] && [ -f "$PYJNIUS_PATH" ]; then
  echo "Найден файл: $PYJNIUS_PATH"
  
  # Создаем резервную копию
  cp "$PYJNIUS_PATH" "$PYJNIUS_PATH.bak"
  
  # Заменяем isinstance(arg, long) на isinstance(arg, int)
  sed -i 's/isinstance(arg, long)/isinstance(arg, int)/g' "$PYJNIUS_PATH"
  
  # Также заменяем другие возможные варианты
  sed -i 's/ isinstance(arg, long)/ isinstance(arg, int)/g' "$PYJNIUS_PATH"
  sed -i 's/(arg, long)/(arg, int)/g' "$PYJNIUS_PATH"
  
  echo "✓ Патч применен к $PYJNIUS_PATH"
  echo "Резервная копия сохранена в $PYJNIUS_PATH.bak"
else
  echo "⚠ Файл jnius_utils.pxi не найден, патч не применен"
  echo "Поиск в других местах:"
  find .buildozer -name "jnius_utils.pxi" 2>/dev/null | head -5 || echo "Файл не найден"
fi
