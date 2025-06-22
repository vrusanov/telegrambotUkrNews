# Розширені функції парсера швейцарських новин

## 🎯 Огляд нових функцій

### 1. 📊 Google Sheets інтеграція
- Автоматичне збереження новин для модерації
- Структурована таблиця з полями: Title, Summary, FullText, Link, Approved
- Workflow модерації з можливістю схвалення/відхилення

### 2. 🖼️ Генерація зображень через DALL-E
- Автоматичне створення зображень на основі синопсису
- Стиль: realistic photo, journalistic, official setting
- Збереження зображень локально

### 3. 📱 Розширений Telegram бот
- Підтримка відправки зображень з текстом
- Методи sendPhoto та sendMessage
- Автоматичне визначення наявності зображення

### 4. 🔄 Інтегрований workflow менеджер
- Повний цикл: парсинг → обробка → збереження → генерація → публікація
- Модульна архітектура з можливістю вимкнення окремих компонентів

## 🚀 Швидкий старт з розширеними функціями

### Крок 1: Встановлення залежностей
```bash
# Оновлені залежності включають Google Sheets API
pip install -r requirements.txt
```

### Крок 2: Налаштування Google Sheets
Дотримуйтесь інструкцій в `GOOGLE_SHEETS_SETUP.md`

### Крок 3: Налаштування змінних середовища
```bash
# Скопіюйте та відредагуйте .env файл
cp .env.example .env

# Додайте ваші API ключі та ID
export OPENAI_API_KEY="your-openai-key"
export GOOGLE_SPREADSHEET_ID="your-spreadsheet-id"
export TELEGRAM_BOT_TOKEN="your-bot-token"
export TELEGRAM_CHAT_ID="your-chat-id"
```

### Крок 4: Запуск розширеного workflow
```bash
# Повний цикл з усіма функціями
python main.py

# Або використовуйте окремі модулі
python news_workflow_manager.py
```

## 📋 Детальний workflow

### 1. Парсинг та обробка (main.py)
```bash
python main.py
```

**Що відбувається:**
- Парсинг RSS-стрічок швейцарських сайтів
- Фільтрація новин про Україну
- GPT-4 обробка (переклад, резюме, класифікація)
- Збереження в Google Sheets з `Approved = No`
- Генерація зображень через DALL-E
- Збереження результатів у JSON

### 2. Модерація (Google Sheets)
1. Відкрийте Google таблицю
2. Перегляньте нові статті
3. Змініть `Approved` на `Yes` для схвалених статей
4. Додайте примітки в колонку `Notes` за потреби

### 3. Публікація схвалених (publish_approved_news.py)
```bash
python publish_approved_news.py
```

**Що відбувається:**
- Читання схвалених статей з Google Sheets
- Генерація зображень для статей (якщо не згенеровано)
- Публікація в Telegram з зображеннями
- Позначення як опубліковано в Google Sheets

## 🔧 Конфігурація модулів

### Google Sheets Manager
```python
from google_sheets_integration import GoogleSheetsManager

manager = GoogleSheetsManager(
    credentials_path="credentials.json",
    spreadsheet_id="your-spreadsheet-id"
)

# Додавання статті
manager.add_article(article)

# Отримання схвалених статей
approved = manager.get_approved_articles()
```

### DALL-E Image Generator
```python
from dalle_image_generator import DALLEImageGenerator

generator = DALLEImageGenerator(
    api_key="your-openai-key",
    images_dir="images"
)

# Генерація зображення
image_path = generator.generate_and_save_image(
    summary="Швейцарія надає допомогу Україні",
    filename="news_image.png"
)
```

### Розширений Telegram бот
```python
from telegram_bot_advanced import TelegramBotAdvanced

bot = TelegramBotAdvanced(
    bot_token="your-bot-token",
    chat_id="your-chat-id"
)

# Відправка з зображенням
bot.send_post_with_image(
    text="Текст новини",
    image_path="path/to/image.png"
)
```

## 📊 Структура Google Sheets

| Колонка | Опис | Редагується |
|---------|------|-------------|
| Timestamp | Дата додавання | Ні |
| Source | Джерело новини | Ні |
| Title | Заголовок українською | Ні |
| Summary | Синопсис | Ні |
| FullText | Повний текст | Ні |
| Link | Посилання на оригінал | Ні |
| **Approved** | **Схвалено (Yes/No)** | **Так** |
| Published | Опубліковано | Ні |
| Notes | Примітки модератора | Так |
| Image_Generated | Згенеровано зображення | Ні |

## 🖼️ DALL-E промпти

### Базовий промпт
```
Generate an image representing: {summary}. 
Style: realistic photo, journalistic, subtle colors, no faces, 
professional news photography, official setting, news-oriented.
```

### Варіації стилів
- **Реалістичний**: `realistic photo, documentary style`
- **Офіційний**: `official setting, formal, professional lighting`
- **Символічний**: `symbolic representation, abstract but clear`
- **Мінімалістичний**: `clean design, subtle colors, minimalist`

## 📱 Telegram функції

### Відправка тільки тексту
```python
bot.send_message("Текст новини")
```

### Відправка з зображенням
```python
bot.send_photo(
    image_path="image.png",
    caption="Підпис до фото"
)
```

### Автоматичний вибір методу
```python
# Автоматично вибере sendPhoto або sendMessage
bot.send_post_with_image(text, image_path)
```

## 🔄 Автоматизація

### Cron для повного циклу
```bash
# Щодня о 9:00 - парсинг та збереження
0 9 * * * cd /path/to/project && python main.py

# Щодня о 12:00 - публікація схвалених
0 12 * * * cd /path/to/project && python publish_approved_news.py
```

### Скрипт автоматизації
```bash
#!/bin/bash
# auto_news_workflow.sh

echo "Запуск парсингу новин..."
python main.py

echo "Очікування модерації (3 години)..."
sleep 10800

echo "Публікація схвалених новин..."
python publish_approved_news.py

echo "Workflow завершено"
```

## 📈 Моніторинг та логи

### Основні лог-файли
- `swiss_news.log` - загальні логи парсера
- `publish_approved.log` - логи публікації
- `dalle_generation.log` - логи генерації зображень

### Команди моніторингу
```bash
# Відстеження парсингу
tail -f swiss_news.log

# Відстеження публікації
tail -f publish_approved.log

# Перевірка згенерованих зображень
ls -la images/

# Статистика Google Sheets
python -c "
from google_sheets_integration import GoogleSheetsManager
manager = GoogleSheetsManager('credentials.json', 'your-id')
approved = manager.get_approved_articles()
print(f'Схвалених статей: {len(approved)}')
"
```

## 🛠️ Troubleshooting

### Google Sheets помилки
```bash
# Тест підключення
python google_sheets_integration.py
```

### DALL-E помилки
```bash
# Тест генерації
python dalle_image_generator.py
```

### Telegram помилки
```bash
# Тест бота
python telegram_bot_advanced.py
```

## 🔒 Безпека

### Файли для .gitignore
```
credentials.json
.env
images/*.png
images/*.jpg
*.log
```

### Рекомендації
1. Регулярно оновлюйте API ключі
2. Обмежте права Service Account
3. Використовуйте різні боти для тестування та продакшену
4. Моніторьте використання API квот

## 📞 Підтримка

Для питань по розширених функціях:
1. Перевірте відповідні лог-файли
2. Запустіть тестові скрипти модулів
3. Перевірте налаштування в .env файлі
4. Переглянте документацію API (Google Sheets, OpenAI, Telegram)
