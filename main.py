"""
Основний скрипт для парсингу швейцарських новин про Україну
"""

import os
import logging
from datetime import datetime
import json
from typing import Optional

from rss_parser import SwissNewsParser, NewsArticle
from config import RSS_FEEDS

# Опціональні імпорти додаткової функціональності
try:
    from telegram_integration import send_news_to_telegram
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False

try:
    from google_sheets_integration import save_articles_to_sheets
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False

try:
    from news_workflow_manager import NewsWorkflowManager, create_workflow_config
    WORKFLOW_MANAGER_AVAILABLE = True
except ImportError:
    WORKFLOW_MANAGER_AVAILABLE = False


def setup_logging():
    """Налаштування логування"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('swiss_news.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


def save_results_to_file(results: dict, filename: str = None):
    """Зберігає результати у файл"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"swiss_news_results_{timestamp}.json"
    
    # Конвертуємо об'єкти NewsArticle в словники для JSON
    json_results = {
        'timestamp': datetime.now().isoformat(),
        'total_articles': len(results['all_articles']),
        'ukraine_articles_count': len(results['ukraine_articles']),
        'processed_articles_count': len(results['processed_articles']),
        'all_articles': [],
        'ukraine_articles': [],
        'processed_articles': []
    }
    
    for category in ['all_articles', 'ukraine_articles', 'processed_articles']:
        for article in results[category]:
            article_dict = {
                'title': article.title,
                'description': article.description,
                'link': article.link,
                'source': article.source,
                'published_date': article.published_date.isoformat() if article.published_date else None,
                'is_ukraine_related': article.is_ukraine_related,
                'translated_title': article.translated_title,
                'translated_text': article.translated_text,
                'summary': article.summary,
                'telegram_post': article.telegram_post
            }
            json_results[category].append(article_dict)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(json_results, f, ensure_ascii=False, indent=2)
    
    print(f"Результати збережено у файл: {filename}")


def print_ukraine_articles(articles: list):
    """Виводить статті про Україну в консоль"""
    if not articles:
        print("Статей про Україну не знайдено.")
        return
    
    print(f"\n{'='*80}")
    print(f"ЗНАЙДЕНО {len(articles)} СТАТЕЙ ПРО УКРАЇНУ")
    print(f"{'='*80}")
    
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. {article.source.upper()}")
        print(f"Заголовок: {article.title}")
        if article.translated_title:
            print(f"Переклад: {article.translated_title}")
        print(f"Опис: {article.description[:200]}...")
        print(f"Посилання: {article.link}")
        print(f"Дата: {article.published_date}")
        
        if article.summary:
            print(f"Резюме: {article.summary}")
        
        if article.telegram_post:
            print(f"\nTelegram-пост:")
            print("-" * 50)
            print(article.telegram_post)
            print("-" * 50)
        
        print()


def main():
    """Основна функція"""
    setup_logging()
    logger = logging.getLogger(__name__)

    print("🇨🇭 Парсер швейцарських новин про Україну")
    print("=" * 50)

    # Перевіряємо доступність розширеної функціональності
    if WORKFLOW_MANAGER_AVAILABLE:
        print("🚀 Використовуємо розширений workflow менеджер")
        run_advanced_workflow()
        return

    # Fallback до базової функціональності
    print("📝 Використовуємо базовий режим")

    # Отримуємо API ключ OpenAI з змінних середовища
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        print("⚠️  УВАГА: Не знайдено OPENAI_API_KEY в змінних середовища.")
        print("Буде виконано тільки базовий парсинг без GPT-обробки.")
        print("Для повної функціональності встановіть змінну середовища:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        print()

    # Створюємо парсер
    parser = SwissNewsParser(openai_api_key)
    
    print("🔍 Починаємо парсинг RSS-стрічок...")
    print(f"Джерела: {', '.join(RSS_FEEDS.keys())}")
    print()
    
    try:
        # Парсимо всі стрічки
        results = parser.parse_all_feeds(hours_back=24)
        
        print(f"📊 Результати парсингу:")
        print(f"   Всього статей за 24 години: {len(results['all_articles'])}")
        print(f"   Статей про Україну: {len(results['ukraine_articles'])}")
        print(f"   Оброблених статей: {len(results['processed_articles'])}")
        
        # Виводимо статті про Україну
        print_ukraine_articles(results['ukraine_articles'])
        
        # Зберігаємо результати
        save_results_to_file(results)

        # Зберігаємо в Google Sheets (якщо налаштовано)
        if GOOGLE_SHEETS_AVAILABLE and results['processed_articles']:
            print("\n📊 Збереження в Google Sheets...")
            sheets_success = save_articles_to_sheets(results['processed_articles'])
            if sheets_success:
                print("✅ Статті збережено в Google Sheets для модерації")
            else:
                print("⚠️ Не вдалося зберегти в Google Sheets")

        # Відправляємо в Telegram (якщо налаштовано)
        if TELEGRAM_AVAILABLE and results['processed_articles']:
            print("\n📱 Відправка в Telegram...")
            telegram_success = send_news_to_telegram(results['processed_articles'])
            if telegram_success:
                print("✅ Новини успішно відправлені в Telegram")
            else:
                print("⚠️ Не вдалося відправити в Telegram (перевірте налаштування)")

        # Виводимо готові Telegram-пости
        processed_articles = results['processed_articles']
        if processed_articles:
            print(f"\n{'='*80}")
            print("ГОТОВІ TELEGRAM-ПОСТИ")
            print(f"{'='*80}")
            
            for i, article in enumerate(processed_articles, 1):
                if article.telegram_post:
                    print(f"\n📱 Пост #{i}:")
                    print("-" * 60)
                    print(article.telegram_post)
                    print("-" * 60)
        
    except Exception as e:
        logger.error(f"Помилка при виконанні парсингу: {e}")
        print(f"❌ Помилка: {e}")


def run_advanced_workflow():
    """Запускає розширений workflow з усіма функціями"""
    try:
        # Створюємо конфігурацію
        config = create_workflow_config()

        # Перевіряємо наявність ключових параметрів
        if not config.get('openai_api_key'):
            print("⚠️  УВАГА: OPENAI_API_KEY не налаштований")
            print("Деякі функції будуть недоступні")

        if not config.get('google_spreadsheet_id'):
            print("⚠️  УВАГА: Google Sheets не налаштовано")
            print("Статті не будуть збережені для модерації")

        if not config.get('telegram_bot_token'):
            print("⚠️  УВАГА: Telegram бот не налаштований")
            print("Автоматична публікація недоступна")

        print("\n🔍 Запускаємо розширений workflow...")

        # Створюємо менеджер workflow
        workflow_manager = NewsWorkflowManager(config)

        # Запускаємо повний цикл (без автоматичної публікації)
        results = workflow_manager.run_full_workflow(
            hours_back=24,
            generate_images=True,
            publish_immediately=False  # Потрібна модерація
        )

        # Виводимо результати
        print("\n" + "="*60)
        print("🎯 РЕЗУЛЬТАТИ РОЗШИРЕНОГО WORKFLOW")
        print("="*60)
        print(f"📰 Знайдено статей: {results.get('parsed_articles', 0)}")
        print(f"🇺🇦 Статей про Україну: {results.get('ukraine_articles', 0)}")
        print(f"🤖 Оброблено GPT: {results.get('processed_articles', 0)}")
        print(f"📊 Збережено в Sheets: {results.get('saved_to_sheets', 0)}")
        print(f"🖼️  Згенеровано зображень: {results.get('generated_images', 0)}")
        print(f"📱 Опубліковано в Telegram: {results.get('published_to_telegram', 0)}")

        if results.get('errors'):
            print(f"\n⚠️  Помилки: {len(results['errors'])}")
            for error in results['errors']:
                print(f"   - {error}")

        print("="*60)

        # Інструкції для подальших дій
        if results.get('saved_to_sheets', 0) > 0:
            print("\n📋 НАСТУПНІ КРОКИ:")
            print("1. Перейдіть до Google Sheets для модерації статей")
            print("2. Змініть 'Approved' на 'Yes' для схвалених статей")
            print("3. Запустіть: python publish_approved_news.py")
            print("4. Схвалені статті будуть опубліковані в Telegram з зображеннями")

    except Exception as e:
        print(f"❌ Помилка розширеного workflow: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
