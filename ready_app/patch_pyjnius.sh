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
  
  echo "Применяем патчи для замены long на int..."
  
  # Заменяем все варианты isinstance(arg, long) на isinstance(arg, int)
  sed -i 's/isinstance(arg, long)/isinstance(arg, int)/g' "$PYJNIUS_PATH"
  
  # Заменяем варианты с пробелом перед isinstance
  sed -i 's/ isinstance(arg, long)/ isinstance(arg, int)/g' "$PYJNIUS_PATH"
  
  # Заменяем варианты в скобках: (isinstance(arg, long)
  sed -i 's/(isinstance(arg, long)/(isinstance(arg, int)/g' "$PYJNIUS_PATH"
  
  # Заменяем варианты с пробелом и скобкой: ( isinstance(arg, long)
  sed -i 's/( isinstance(arg, long)/( isinstance(arg, int)/g' "$PYJNIUS_PATH"
  
  # Заменяем простые варианты (arg, long)
  sed -i 's/(arg, long)/(arg, int)/g' "$PYJNIUS_PATH"
  
  # Заменяем варианты с пробелом: ( arg, long)
  sed -i 's/( arg, long)/( arg, int)/g' "$PYJNIUS_PATH"
  
  # Заменяем сложные выражения типа: (isinstance(arg, long) and ...)
  # Используем более общий паттерн для замены long в контексте isinstance
  sed -i 's/isinstance([^,]*,\s*long\b)/isinstance(\1, int)/g' "$PYJNIUS_PATH"
  
  # Проверяем, были ли сделаны замены
  if grep -q "long" "$PYJNIUS_PATH"; then
    echo "⚠ Предупреждение: В файле все еще есть вхождения 'long'"
    echo "Оставшиеся вхождения:"
    grep -n "long" "$PYJNIUS_PATH" | head -5
  else
    echo "✓ Все вхождения 'long' заменены на 'int'"
  fi
  
  echo "✓ Патч применен к $PYJNIUS_PATH"
  echo "Резервная копия сохранена в $PYJNIUS_PATH.bak"
else
  echo "⚠ Файл jnius_utils.pxi не найден, патч не применен"
  echo "Поиск в других местах:"
  find .buildozer -name "jnius_utils.pxi" 2>/dev/null | head -5 || echo "Файл не найден"
fi
