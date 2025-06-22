#!/bin/bash

# Скрипт для налаштування автоматичного запуску парсера

echo "🔧 Налаштування автоматичного запуску парсера швейцарських новин"
echo "================================================================"

# Отримуємо поточну директорію
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📁 Директорія проекту: $SCRIPT_DIR"

# Перевіряємо наявність Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не знайдено. Встановіть Python3 перед продовженням."
    exit 1
fi

# Перевіряємо наявність pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 не знайдено. Встановіть pip3 перед продовженням."
    exit 1
fi

# Встановлюємо залежності
echo "📦 Встановлення залежностей..."
pip3 install -r "$SCRIPT_DIR/requirements.txt"

if [ $? -ne 0 ]; then
    echo "❌ Помилка при встановленні залежностей"
    exit 1
fi

# Перевіряємо API ключ
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  УВАГА: Змінна середовища OPENAI_API_KEY не встановлена"
    echo "Для повної функціональності встановіть її:"
    echo "export OPENAI_API_KEY='your-api-key-here'"
    echo "Або додайте в ~/.bashrc або ~/.zshrc"
    echo ""
    read -p "Продовжити без API ключа? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Створюємо скрипт-обгортку для cron
WRAPPER_SCRIPT="$SCRIPT_DIR/run_parser.sh"
cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash

# Скрипт-обгортка для запуску парсера з cron

# Встановлюємо робочу директорію
cd "$SCRIPT_DIR"

# Встановлюємо змінні середовища (якщо потрібно)
# export OPENAI_API_KEY="your-api-key-here"

# Логування
LOG_FILE="$SCRIPT_DIR/cron.log"
echo "\$(date): Запуск парсера швейцарських новин" >> "\$LOG_FILE"

# Запускаємо парсер
python3 "$SCRIPT_DIR/main.py" >> "\$LOG_FILE" 2>&1

# Логування завершення
echo "\$(date): Парсер завершив роботу" >> "\$LOG_FILE"
echo "----------------------------------------" >> "\$LOG_FILE"
EOF

# Робимо скрипт виконуваним
chmod +x "$WRAPPER_SCRIPT"

echo "✅ Створено скрипт-обгортку: $WRAPPER_SCRIPT"

# Пропонуємо налаштувати cron
echo ""
echo "🕒 Налаштування cron job..."
echo "Виберіть частоту запуску:"
echo "1) Щодня о 9:00 ранку"
echo "2) Двічі на день (9:00 та 21:00)"
echo "3) Кожні 6 годин"
echo "4) Власний розклад"
echo "5) Пропустити налаштування cron"

read -p "Ваш вибір (1-5): " choice

case $choice in
    1)
        CRON_SCHEDULE="0 9 * * *"
        CRON_DESCRIPTION="щодня о 9:00"
        ;;
    2)
        CRON_SCHEDULE="0 9,21 * * *"
        CRON_DESCRIPTION="двічі на день о 9:00 та 21:00"
        ;;
    3)
        CRON_SCHEDULE="0 */6 * * *"
        CRON_DESCRIPTION="кожні 6 годин"
        ;;
    4)
        echo "Введіть cron розклад (формат: хвилина година день місяць день_тижня):"
        read -p "Приклад: 0 9 * * * (щодня о 9:00): " CRON_SCHEDULE
        CRON_DESCRIPTION="за вашим розкладом"
        ;;
    5)
        echo "⏭️  Пропускаємо налаштування cron"
        echo "Ви можете запустити парсер вручну: $WRAPPER_SCRIPT"
        exit 0
        ;;
    *)
        echo "❌ Невірний вибір"
        exit 1
        ;;
esac

# Додаємо cron job
CRON_JOB="$CRON_SCHEDULE $WRAPPER_SCRIPT"

# Перевіряємо, чи вже існує такий job
if crontab -l 2>/dev/null | grep -q "$WRAPPER_SCRIPT"; then
    echo "⚠️  Cron job для цього скрипта вже існує"
    read -p "Замінити існуючий? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Видаляємо старий job
        crontab -l 2>/dev/null | grep -v "$WRAPPER_SCRIPT" | crontab -
    else
        echo "🚫 Залишаємо існуючий cron job"
        exit 0
    fi
fi

# Додаємо новий job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Cron job успішно додано!"
    echo "📅 Розклад: $CRON_DESCRIPTION"
    echo "🔧 Команда: $CRON_JOB"
    echo ""
    echo "📋 Поточні cron jobs:"
    crontab -l | grep "$WRAPPER_SCRIPT"
else
    echo "❌ Помилка при додаванні cron job"
    exit 1
fi

echo ""
echo "🎉 Налаштування завершено!"
echo ""
echo "📝 Корисні команди:"
echo "   Переглянути cron jobs: crontab -l"
echo "   Видалити cron job: crontab -e"
echo "   Переглянути логи: tail -f $SCRIPT_DIR/cron.log"
echo "   Запустити вручну: $WRAPPER_SCRIPT"
echo ""
echo "📁 Результати будуть збережені в: $SCRIPT_DIR"
