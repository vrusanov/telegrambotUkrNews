"""
Головний файл MVP telegram-news-ua-ch
Точка входу з усім пайплайном згідно з технічними вимогами
"""

import os
import logging
from datetime import datetime
from typing import List

# Імпорти наших модулів
from parser import NewsParser, Article
from translate import Translator
from summary import Summarizer
from telegram_client import TelegramClient

# Конфігурація функцій (легко ввімкнути/вимкнути)
# Для ввімкнення OpenAI функцій:
# 1. Поповніть баланс OpenAI або створіть новий API ключ
# 2. Оновіть OPENAI_API_KEY в GitHub Secrets
# 3. Змініть False на True для потрібних функцій
USE_GPT_CLASSIFICATION = False  # Встановіть True коли є OpenAI квота
USE_TRANSLATION = False         # Встановіть True для перекладу українською
USE_SUMMARIZATION = False       # Встановіть True для створення синопсису


def setup_logging():
    """Налаштування логування у консоль + файл"""
    # Створюємо директорію для логів
    os.makedirs("logs", exist_ok=True)
    
    # Налаштування логування
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


def load_environment_variables() -> dict:
    """Завантажує змінні середовища"""
    config = {
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'telegram_token': os.getenv('TELEGRAM_TOKEN'),
        'telegram_channel': os.getenv('TELEGRAM_CHANNEL')
    }
    
    missing_vars = [key for key, value in config.items() if not value]
    if missing_vars:
        raise ValueError(f"Відсутні змінні середовища: {missing_vars}")
    
    return config


def process_article(article: Article, translator: Translator, 
                   summarizer: Summarizer) -> dict:
    """
    Обробляє одну статтю: класифікація → переклад → резюме
    
    Args:
        article: Стаття для обробки
        translator: Перекладач
        summarizer: Резюматор
        
    Returns:
        Словник з обробленими даними
    """
    logger = logging.getLogger(__name__)
    
    logger.info(f"Обробляємо статтю: {article.title}")
    
    # Крок 1: Додаткова GPT класифікація (якщо ввімкнено)
    if USE_GPT_CLASSIFICATION:
        text_for_classification = f"{article.title}\n{article.description}"
        if article.full_text:
            text_for_classification += f"\n{article.full_text[:500]}"

        classification = translator.classify_ukraine_related(text_for_classification)

        if classification != "Ukraine-related":
            logger.info(f"Стаття не про Україну за GPT класифікацією: {article.title}")
            return None

        logger.info(f"✅ GPT підтвердив: стаття про Україну - {article.title}")
    else:
        logger.info(f"Пропускаємо GPT класифікацію (вимкнено) для: {article.title}")
    
    # Крок 2: Переклад українською (якщо ввімкнено)
    if USE_TRANSLATION:
        logger.info(f"Перекладаємо з мови: {article.language}")

        title_ua = translator.translate_to_ukrainian(article.title, article.language)
        description_ua = translator.translate_to_ukrainian(article.description, article.language)

        full_text_ua = None
        if article.full_text:
            full_text_ua = translator.translate_to_ukrainian(article.full_text, article.language)

        if not title_ua:
            logger.error(f"Не вдалося перекласти заголовок: {article.title}")
            return None
    else:
        logger.info(f"Використовуємо оригінальний текст ({article.language})")
        title_ua = article.title
        description_ua = article.description
        full_text_ua = article.full_text

    # Крок 3: Створення синопсису (якщо ввімкнено)
    if USE_SUMMARIZATION:
        text_for_summary = full_text_ua or description_ua or ""
        summary_ua = summarizer.create_summary_from_parts(
            title_ua, description_ua, text_for_summary
        )

        if not summary_ua:
            logger.warning(f"Не вдалося створити синопсис для: {title_ua}")
            summary_ua = description_ua or "Короткий опис недоступний"
        else:
            logger.info("✅ Синопсис створено")
    else:
        logger.info("Використовуємо оригінальний опис (резюмування вимкнено)")
        summary_ua = description_ua or "Короткий опис недоступний"
    
    return {
        'title': title_ua,
        'summary': summary_ua,
        'full_text': full_text_ua or description_ua,
        'url': article.url,
        'source': article.source,
        'original_language': article.language
    }


def main():
    """Основна функція пайплайну"""
    # Налаштування логування
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Запуск telegram-news-ua-ch MVP")

    # Показуємо поточну конфігурацію
    logger.info("⚙️ Конфігурація:")
    logger.info(f"   - GPT класифікація: {'✅ Ввімкнено' if USE_GPT_CLASSIFICATION else '❌ Вимкнено'}")
    logger.info(f"   - Переклад: {'✅ Ввімкнено' if USE_TRANSLATION else '❌ Вимкнено'}")
    logger.info(f"   - Резюмування: {'✅ Ввімкнено' if USE_SUMMARIZATION else '❌ Вимкнено'}")

    try:
        # Завантаження конфігурації
        config = load_environment_variables()
        logger.info("✅ Змінні середовища завантажено")
        
        # Ініціалізація компонентів
        parser = NewsParser()
        translator = Translator(config['openai_api_key'])
        summarizer = Summarizer(config['openai_api_key'])
        telegram_client = TelegramClient(
            config['telegram_token'], 
            config['telegram_channel']
        )
        
        logger.info("✅ Компоненти ініціалізовано")
        
        # Тест Telegram з'єднання
        if not telegram_client.test_connection():
            raise Exception("Не вдалося підключитися до Telegram")
        
        # КРОК 1: Парсинг RSS-стрічок
        logger.info("📡 Парсинг RSS-стрічок...")
        ukraine_articles = parser.parse_all_feeds()
        
        if not ukraine_articles:
            logger.info("📭 Нових статей про Україну не знайдено")
            return
        
        logger.info(f"📰 Знайдено {len(ukraine_articles)} статей про Україну")
        
        # КРОК 2: Завантаження повного тексту
        logger.info("📄 Завантаження повного тексту...")
        articles_with_text = parser.get_articles_with_full_text(ukraine_articles)
        
        # КРОК 3-5: Обробка статей (класифікація → переклад → резюме)
        logger.info("🔄 Обробка статей...")
        processed_articles = []
        
        for article in articles_with_text:
            try:
                processed_data = process_article(article, translator, summarizer)
                if processed_data:
                    processed_articles.append(processed_data)
            except Exception as e:
                logger.error(f"Помилка обробки статті {article.title}: {e}")
        
        if not processed_articles:
            logger.info("📭 Немає статей для публікації після обробки")
            return
        
        logger.info(f"✅ Оброблено {len(processed_articles)} статей")
        
        # КРОК 6: Публікація в Telegram
        logger.info("📱 Публікація в Telegram...")
        published_count = 0
        
        for article_data in processed_articles:
            try:
                message_id = telegram_client.send_message(
                    title=article_data['title'],
                    summary=article_data['summary'],
                    full_text=article_data['full_text'],
                    url=article_data['url'],
                    source=article_data['source']
                )
                
                if message_id:
                    published_count += 1
                    logger.info(f"✅ Опубліковано: {article_data['title']} (ID: {message_id})")
                else:
                    logger.warning(f"⚠️ Не опубліковано: {article_data['title']}")
                
                # Затримка між публікаціями
                import time
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"Помилка публікації {article_data['title']}: {e}")
        
        # Підсумок
        logger.info("🎉 Пайплайн завершено")
        logger.info(f"📊 Статистика:")
        logger.info(f"   - Знайдено статей про Україну: {len(ukraine_articles)}")
        logger.info(f"   - Успішно оброблено: {len(processed_articles)}")
        logger.info(f"   - Опубліковано в Telegram: {published_count}")
        
    except Exception as e:
        logger.error(f"❌ Критична помилка: {e}")
        raise


if __name__ == "__main__":
    main()
