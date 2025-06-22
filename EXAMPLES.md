# Приклади використання розширених функцій

## 🚀 Швидкий старт з усіма функціями

### 1. Повний workflow з модерацією
```bash
# Крок 1: Парсинг та збереження в Google Sheets
python main.py

# Крок 2: Модерація в Google Sheets (вручну)
# Змініть "Approved" на "Yes" для схвалених статей

# Крок 3: Публікація схвалених з зображеннями
python publish_approved_news.py
```

### 2. Тестування окремих компонентів
```bash
# Тест Google Sheets
python google_sheets_integration.py

# Тест DALL-E генерації
python dalle_image_generator.py

# Тест розширеного Telegram бота
python telegram_bot_advanced.py

# Тест повного workflow
python news_workflow_manager.py
```

## 📊 Google Sheets інтеграція

### Базове використання
```python
from google_sheets_integration import GoogleSheetsManager
from rss_parser import NewsArticle
from datetime import datetime
import pytz

# Ініціалізація
manager = GoogleSheetsManager(
    credentials_path="credentials.json",
    spreadsheet_id="your-spreadsheet-id"
)

# Створення тестової статті
article = NewsArticle(
    title="Test Article",
    description="Test description", 
    link="https://example.com",
    source="test",
    published_date=datetime.now(pytz.UTC)
)
article.translated_title = "Тестова стаття"
article.summary = "Короткий синопсис"
article.translated_text = "Повний текст українською"

# Додавання статті
success = manager.add_article(article)
print(f"Стаття додана: {success}")

# Отримання схвалених статей
approved = manager.get_approved_articles()
print(f"Схвалених статей: {len(approved)}")
```

### Робота з кількома статтями
```python
# Додавання кількох статей
articles = [article1, article2, article3]
added_count = manager.add_articles_batch(articles)
print(f"Додано {added_count} статей")

# Отримання неопублікованих схвалених
unpublished = manager.get_unpublished_approved_articles()
for article in unpublished:
    print(f"- {article['Title']}")
```

## 🖼️ DALL-E генерація зображень

### Базова генерація
```python
from dalle_image_generator import DALLEImageGenerator

# Ініціалізація
generator = DALLEImageGenerator(
    api_key="your-openai-key",
    images_dir="images"
)

# Генерація зображення
summary = "Швейцарія надає гуманітарну допомогу Україні"
image_path = generator.generate_and_save_image(
    summary=summary,
    filename="news_image.png"
)

if image_path:
    print(f"Зображення збережено: {image_path}")
```

### Кастомні промпти
```python
# Створення власного промпту
custom_prompt = generator.generate_news_prompt(
    summary="Українські біженці в Швейцарії",
    style="documentary photography"
)
print(f"Промпт: {custom_prompt}")

# Генерація з кастомним промптом
image_url = generator.generate_image(
    prompt=custom_prompt,
    size="1792x1024",
    quality="hd"
)
```

### Варіації стилів
```python
from dalle_image_generator import create_news_prompt_variations

summary = "Зустріч швейцарських та українських дипломатів"
variations = create_news_prompt_variations(summary)

for i, prompt in enumerate(variations):
    print(f"Варіант {i+1}: {prompt[:100]}...")
```

## 📱 Розширений Telegram бот

### Відправка з зображенням
```python
from telegram_bot_advanced import TelegramBotAdvanced

# Ініціалізація
bot = TelegramBotAdvanced(
    bot_token="your-bot-token",
    chat_id="your-chat-id"
)

# Тест з'єднання
if bot.test_connection():
    print("Бот підключено успішно")

# Відправка тільки тексту
result = bot.send_message("Тестове повідомлення")

# Відправка фото з підписом
result = bot.send_photo(
    image_path="images/news_image.png",
    caption="📢 *Новина з зображенням*\n\nОпис новини...",
    parse_mode="Markdown"
)

# Автоматичний вибір методу
result = bot.send_post_with_image(
    text="Текст новини",
    image_path="images/news_image.png"  # Якщо файл існує - відправить фото
)
```

### Пакетна відправка
```python
from telegram_bot_advanced import send_news_batch_with_images

news_data = [
    {
        "title": "Новина 1",
        "text": "📢 *Заголовок 1*\n\nТекст новини 1..."
    },
    {
        "title": "Новина 2", 
        "text": "📢 *Заголовок 2*\n\nТекст новини 2..."
    }
]

sent_count = send_news_batch_with_images(
    news_data=news_data,
    images_dir="images"
)
print(f"Відправлено {sent_count} новин")
```

## 🔄 Workflow менеджер

### Повний цикл
```python
from news_workflow_manager import NewsWorkflowManager, create_workflow_config

# Створення конфігурації з змінних середовища
config = create_workflow_config()

# Ініціалізація менеджера
workflow = NewsWorkflowManager(config)

# Запуск повного циклу
results = workflow.run_full_workflow(
    hours_back=24,
    generate_images=True,
    publish_immediately=False  # Потрібна модерація
)

# Виведення результатів
print(f"Знайдено статей: {results['parsed_articles']}")
print(f"Про Україну: {results['ukraine_articles']}")
print(f"Оброблено: {results['processed_articles']}")
print(f"Збережено в Sheets: {results['saved_to_sheets']}")
print(f"Згенеровано зображень: {results['generated_images']}")
```

### Окремі кроки workflow
```python
# Тільки парсинг
parse_results = workflow.parse_and_process_news(hours_back=24)

# Тільки збереження в Google Sheets
articles = parse_results.get('processed_articles', [])
workflow.save_to_sheets(articles)

# Тільки генерація зображень
images = workflow.generate_images_for_articles(articles)

# Тільки публікація в Telegram
published = workflow.publish_to_telegram(articles, images)
```

## 📋 Публікація схвалених новин

### Автоматична публікація
```python
from publish_approved_news import ApprovedNewsPublisher

# Конфігурація
config = {
    'google_credentials_path': 'credentials.json',
    'google_spreadsheet_id': 'your-spreadsheet-id',
    'telegram_bot_token': 'your-bot-token',
    'telegram_chat_id': 'your-chat-id',
    'openai_api_key': 'your-openai-key',
    'images_dir': 'images'
}

# Ініціалізація публікатора
publisher = ApprovedNewsPublisher(config)

# Публікація всіх схвалених статей
results = publisher.publish_all_approved(max_articles=5)

print(f"Знайдено: {results['total_found']}")
print(f"Опубліковано: {results['published']}")
print(f"Помилки: {results['failed']}")
```

### Публікація однієї статті
```python
# Отримання схвалених статей
approved_articles = publisher.get_approved_articles()

if approved_articles:
    article = approved_articles[0]
    row_number = 2  # Номер рядка в Google Sheets
    
    success = publisher.publish_article(article, row_number)
    if success:
        print("Стаття опублікована успішно")
```

## 🛠️ Кастомізація та розширення

### Власний промпт для DALL-E
```python
def custom_dalle_prompt(summary, style="realistic"):
    return f"""
    Create a professional news image about: {summary}
    
    Style requirements:
    - {style} photography
    - Swiss setting if applicable
    - Neutral, journalistic perspective
    - High quality, professional lighting
    - No faces, no text overlays
    - Subtle, muted colors
    - Documentary style composition
    """

# Використання
generator = DALLEImageGenerator("your-key")
prompt = custom_dalle_prompt("Швейцарська допомога Україні")
image_url = generator.generate_image(prompt)
```

### Власний формат Telegram посту
```python
def create_custom_telegram_post(article_data):
    title = article_data.get('Title', '')
    summary = article_data.get('Summary', '')
    link = article_data.get('Link', '')
    source = article_data.get('Source', '')
    
    post = f"""
🇨🇭🇺🇦 *{title}*

📝 {summary}

🔗 [Читати повністю]({link})
📰 Джерело: {source}

#Швейцарія #Україна #Новини
    """.strip()
    
    return post

# Використання в публікаторі
class CustomPublisher(ApprovedNewsPublisher):
    def create_telegram_post(self, article):
        return create_custom_telegram_post(article)
```

### Додавання нових RSS джерел
```python
# В config.py
RSS_FEEDS = {
    'swissinfo': 'https://www.swissinfo.ch/rss',
    '20min': 'https://www.20min.ch/rss',
    'letemps': 'https://www.letemps.ch/rss',
    'nzz': 'https://www.nzz.ch/recent.rss',  # Додаткове джерело
    'srf': 'https://www.srf.ch/news/bnf/rss/1646'  # Ще одне джерело
}
```

## 🔧 Налагодження та тестування

### Тестування Google Sheets
```python
import os
from google_sheets_integration import GoogleSheetsManager

try:
    manager = GoogleSheetsManager(
        'credentials.json',
        os.getenv('GOOGLE_SPREADSHEET_ID')
    )
    print("✅ Google Sheets підключено")
    
    # Тест запису
    records = manager.worksheet.get_all_records()
    print(f"Записів в таблиці: {len(records)}")
    
except Exception as e:
    print(f"❌ Помилка Google Sheets: {e}")
```

### Тестування DALL-E
```python
from dalle_image_generator import generate_image_for_news

image_path = generate_image_for_news(
    summary="Тестовий синопсис для генерації",
    output_path="test_image.png"
)

if image_path:
    print(f"✅ Зображення згенеровано: {image_path}")
else:
    print("❌ Не вдалося згенерувати зображення")
```

### Тестування Telegram
```python
from telegram_bot_advanced import publish_to_telegram

success = publish_to_telegram(
    text="🧪 Тестове повідомлення",
    image_path="test_image.png"
)

if success:
    print("✅ Повідомлення відправлено")
else:
    print("❌ Помилка відправки")
```

## 📈 Моніторинг та аналітика

### Статистика роботи
```python
import json
from datetime import datetime, timedelta

# Аналіз результатів за останні дні
def analyze_results(days=7):
    stats = {
        'total_articles': 0,
        'ukraine_articles': 0,
        'published_articles': 0,
        'generated_images': 0
    }
    
    # Читання файлів результатів
    import glob
    result_files = glob.glob('swiss_news_results_*.json')
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for file_path in result_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            file_date = datetime.fromisoformat(data['timestamp'])
            if file_date >= cutoff_date:
                stats['total_articles'] += data.get('total_articles', 0)
                stats['ukraine_articles'] += data.get('ukraine_articles_count', 0)
                # Додайте інші метрики
                
        except Exception as e:
            print(f"Помилка читання {file_path}: {e}")
    
    return stats

# Використання
stats = analyze_results(days=7)
print(f"Статистика за 7 днів: {stats}")
```
