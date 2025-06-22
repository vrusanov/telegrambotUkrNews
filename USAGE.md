# Інструкція з використання парсера швейцарських новин

## Швидкий старт

### 1. Підготовка середовища

```bash
# Створення віртуального середовища
python3 -m venv venv

# Активація віртуального середовища
source venv/bin/activate  # Linux/Mac
# або
venv\Scripts\activate     # Windows

# Встановлення залежностей
pip install -r requirements.txt
```

### 2. Налаштування API ключа (опціонально)

Для повної функціональності з GPT-4:

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

Або створіть файл `.env`:
```bash
cp .env.example .env
# Відредагуйте .env файл та додайте ваш API ключ
```

### 3. Запуск

```bash
# Базовий запуск
python main.py

# Запуск тестів
python test_parser.py

# Автоматичне налаштування cron
./setup_cron.sh
```

## Детальне використання

### Основні команди

```bash
# Парсинг з виводом у консоль
python main.py

# Тестування функціональності
python test_parser.py

# Налаштування автоматичного запуску
chmod +x setup_cron.sh
./setup_cron.sh
```

### Структура результатів

Скрипт створює JSON файли з результатами:
```json
{
  "timestamp": "2025-06-22T13:01:42.516Z",
  "total_articles": 0,
  "ukraine_articles_count": 0,
  "processed_articles_count": 0,
  "all_articles": [...],
  "ukraine_articles": [...],
  "processed_articles": [...]
}
```

### Налаштування RSS джерел

Відредагуйте `config.py` для додавання нових джерел:

```python
RSS_FEEDS = {
    'swissinfo': 'https://www.swissinfo.ch/rss',
    '20min': 'https://www.20min.ch/rss',
    'letemps': 'https://www.letemps.ch/rss',
    'new_source': 'https://example.com/rss'  # Додайте нове джерело
}
```

### Налаштування ключових слів

```python
UKRAINE_KEYWORDS = [
    "Україна", "українці", "Ukraine", "Ukrainer", "Ukrainiens",
    "Kyiv", "Kiev", "Zelensky", "Zelenskyy", "Зеленський",
    "your_keyword"  # Додайте нові ключові слова
]
```

## Автоматизація

### Cron налаштування

```bash
# Запуск setup_cron.sh для інтерактивного налаштування
./setup_cron.sh

# Або додайте вручну в crontab:
crontab -e

# Додайте рядок (приклад - щодня о 9:00):
0 9 * * * /path/to/urk-news/run_parser.sh
```

### Варіанти розкладу

- `0 9 * * *` - щодня о 9:00
- `0 9,21 * * *` - двічі на день (9:00 та 21:00)
- `0 */6 * * *` - кожні 6 годин
- `*/30 * * * *` - кожні 30 хвилин

## Моніторинг

### Логи

```bash
# Перегляд логів парсера
tail -f swiss_news.log

# Перегляд логів cron
tail -f cron.log
```

### Перевірка статусу

```bash
# Перевірка cron jobs
crontab -l

# Перевірка останніх результатів
ls -la swiss_news_results_*.json

# Перевірка віртуального середовища
source venv/bin/activate
pip list
```

## Troubleshooting

### Проблеми з залежностями

```bash
# Оновлення pip
pip install --upgrade pip

# Переустановка залежностей
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### Проблеми з RSS

- Перевірте доступність URL
- Деякі сайти можуть блокувати автоматичні запити
- Спробуйте змінити User-Agent в `rss_parser.py`

### Проблеми з GPT

- Перевірте правильність API ключа
- Перевірте баланс на OpenAI акаунті
- Перевірте ліміти запитів

### Проблеми з cron

```bash
# Перевірка статусу cron сервісу
sudo systemctl status cron  # Linux
sudo launchctl list | grep cron  # Mac

# Перевірка прав доступу
chmod +x run_parser.sh
chmod +x setup_cron.sh
```

## Розширення функціональності

### Додавання нових мов

Відредагуйте `UKRAINE_KEYWORDS` в `config.py`:

```python
UKRAINE_KEYWORDS = [
    # Українська
    "Україна", "українці", "Зеленський",
    # Англійська  
    "Ukraine", "Ukrainians", "Zelensky",
    # Німецька
    "Ukraine", "Ukrainer", "Selenskyj",
    # Французька
    "Ukraine", "Ukrainiens", "Zelensky",
    # Італійська
    "Ucraina", "ucraini", "Zelensky"
]
```

### Додавання Telegram інтеграції

Створіть Telegram бота та додайте в `.env`:

```bash
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### Додавання email сповіщень

Встановіть додаткові залежності:

```bash
pip install smtplib email
```

## Підтримка

Для питань та проблем:
1. Перевірте логи
2. Запустіть тести
3. Перевірте документацію
4. Створіть issue в репозиторії
