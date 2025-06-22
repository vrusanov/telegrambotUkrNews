"""
Інтегрований скрипт, який виконує всі кроки технічного завдання:
парсинг → фільтрація → переклад → резюме → збереження → публікація
"""

import os
import logging
from datetime import datetime
from typing import List, Optional

# Імпорти наших модулів
from parse_news import SwissNewsParser, NewsArticleWithLang, classify_with_gpt
from translation_service import TranslationService
from gpt_processor import GPTProcessor

# Опціональні імпорти
try:
    from google_sheets_integration import save_articles_to_sheets
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False

try:
    from telegram_bot_advanced import publish_to_telegram
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False

try:
    from dalle_image_generator import generate_image_for_news
    DALLE_AVAILABLE = True
except ImportError:
    DALLE_AVAILABLE = False

logger = logging.getLogger(__name__)


class IntegratedNewsProcessor:
    """Інтегрований процесор новин, який виконує всі кроки workflow"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Ініціалізація процесора
        
        Args:
            openai_api_key: OpenAI API ключ
        """
        self.openai_api_key = openai_api_key
        
        # Ініціалізуємо компоненти
        self.news_parser = SwissNewsParser()
        self.translation_service = None
        self.gpt_processor = None
        
        if openai_api_key:
            self.translation_service = TranslationService(openai_api_key)
            self.gpt_processor = GPTProcessor(openai_api_key)
            logger.info("Ініціалізовано з GPT підтримкою")
        else:
            logger.warning("Ініціалізовано без GPT підтримки")
    
    def step_3_parse_news(self) -> List[NewsArticleWithLang]:
        """
        КРОК 3: Парсинг новин за сьогодні з визначенням мови
        
        Returns:
            Список статей за сьогодні
        """
        logger.info("=== КРОК 3: Парсинг новин ===")
        
        results = self.news_parser.parse_all_feeds_today()
        all_articles = results['all_articles']
        
        logger.info(f"Знайдено {len(all_articles)} статей за сьогодні")
        
        # Виводимо статистику по мовах
        language_stats = {}
        for article in all_articles:
            lang = article.detected_language or 'unknown'
            language_stats[lang] = language_stats.get(lang, 0) + 1
        
        logger.info(f"Статистика мов: {language_stats}")
        
        return all_articles
    
    def step_4_filter_ukraine_news(self, articles: List[NewsArticleWithLang]) -> List[NewsArticleWithLang]:
        """
        КРОК 4: Фільтрація новин про Україну + GPT класифікація
        
        Args:
            articles: Список всіх статей
            
        Returns:
            Список статей про Україну
        """
        logger.info("=== КРОК 4: Фільтрація новин про Україну ===")
        
        ukraine_articles = []
        
        for article in articles:
            # Перевірка ключових слів
            if article.is_ukraine_related:
                ukraine_articles.append(article)
                logger.info(f"Знайдено за ключовими словами: {article.title}")
            elif self.gpt_processor:
                # Додаткова перевірка через GPT
                classification = classify_with_gpt(article, self.gpt_processor)
                if classification == "Ukraine-related":
                    article.is_ukraine_related = True
                    ukraine_articles.append(article)
                    logger.info(f"Знайдено через GPT: {article.title}")
        
        logger.info(f"Всього знайдено {len(ukraine_articles)} статей про Україну")
        return ukraine_articles
    
    def step_5_fetch_full_text(self, articles: List[NewsArticleWithLang]) -> List[NewsArticleWithLang]:
        """
        КРОК 5: Отримання повного тексту статей
        
        Args:
            articles: Список статей
            
        Returns:
            Список статей з повним текстом
        """
        logger.info("=== КРОК 5: Отримання повного тексту ===")
        
        return self.news_parser.get_articles_with_full_text(articles)
    
    def step_6_translate_articles(self, articles: List[NewsArticleWithLang]) -> List[NewsArticleWithLang]:
        """
        КРОК 6: Переклад статей українською з урахуванням мови
        
        Args:
            articles: Список статей
            
        Returns:
            Список перекладених статей
        """
        logger.info("=== КРОК 6: Переклад українською ===")
        
        if not self.translation_service:
            logger.warning("Сервіс перекладу недоступний")
            return articles
        
        translated_articles = []
        
        for article in articles:
            try:
                logger.info(f"Перекладаємо: {article.title} [{article.detected_language}]")
                translated_article = self.translation_service.translate_article(article)
                translated_articles.append(translated_article)
            except Exception as e:
                logger.error(f"Помилка перекладу статті {article.title}: {e}")
                translated_articles.append(article)  # Додаємо оригінал
        
        return translated_articles
    
    def step_7_create_summaries(self, articles: List[NewsArticleWithLang]) -> List[NewsArticleWithLang]:
        """
        КРОК 7: Створення синопсисів
        
        Args:
            articles: Список перекладених статей
            
        Returns:
            Список статей з синопсисами
        """
        logger.info("=== КРОК 7: Створення синопсисів ===")
        
        if not self.translation_service:
            logger.warning("Сервіс перекладу недоступний")
            return articles
        
        for article in articles:
            try:
                text_for_summary = (
                    article.translated_text or 
                    article.translated_description or 
                    article.description
                )
                
                if text_for_summary:
                    summary = self.translation_service.summarize_article(text_for_summary)
                    if summary:
                        article.summary = summary
                        logger.info(f"Створено синопсис для: {article.title}")
                
            except Exception as e:
                logger.error(f"Помилка створення синопсису для {article.title}: {e}")
        
        return articles
    
    def step_8_save_to_google_sheets(self, articles: List[NewsArticleWithLang]) -> bool:
        """
        КРОК 8: Збереження в Google Sheets
        
        Args:
            articles: Список оброблених статей
            
        Returns:
            True якщо успішно збережено
        """
        logger.info("=== КРОК 8: Збереження в Google Sheets ===")
        
        if not GOOGLE_SHEETS_AVAILABLE:
            logger.warning("Google Sheets інтеграція недоступна")
            return False
        
        # Конвертуємо в стандартний формат NewsArticle
        from rss_parser import NewsArticle
        standard_articles = []
        
        for article in articles:
            standard_article = NewsArticle(
                title=article.title,
                description=article.description,
                link=article.link,
                source=article.source,
                published_date=article.published_date
            )
            
            # Копіюємо перекладені поля
            standard_article.translated_title = getattr(article, 'translated_title', None)
            standard_article.translated_text = getattr(article, 'translated_text', None)
            standard_article.summary = getattr(article, 'summary', None)
            
            standard_articles.append(standard_article)
        
        return save_articles_to_sheets(standard_articles)
    
    def step_9_publish_to_telegram(self, articles: List[NewsArticleWithLang]) -> int:
        """
        КРОК 9: Публікація в Telegram
        
        Args:
            articles: Список оброблених статей
            
        Returns:
            Кількість опублікованих статей
        """
        logger.info("=== КРОК 9: Публікація в Telegram ===")
        
        if not TELEGRAM_AVAILABLE:
            logger.warning("Telegram інтеграція недоступна")
            return 0
        
        published_count = 0
        
        for article in articles:
            try:
                # Створюємо Telegram пост
                telegram_post = self._create_telegram_post(article)
                
                # Генеруємо зображення (якщо доступно)
                image_path = None
                if DALLE_AVAILABLE and article.summary and self.openai_api_key:
                    try:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"news_{published_count+1}_{timestamp}.png"
                        image_path = generate_image_for_news(
                            article.summary, 
                            f"images/{filename}",
                            self.openai_api_key
                        )
                    except Exception as e:
                        logger.warning(f"Не вдалося згенерувати зображення: {e}")
                
                # Публікуємо
                success = publish_to_telegram(telegram_post, image_path)
                if success:
                    published_count += 1
                    logger.info(f"Опубліковано: {article.title}")
                
                # Затримка між публікаціями
                import time
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Помилка публікації {article.title}: {e}")
        
        logger.info(f"Опубліковано {published_count} з {len(articles)} статей")
        return published_count
    
    def _create_telegram_post(self, article: NewsArticleWithLang) -> str:
        """Створює Telegram пост з статті"""
        title = article.translated_title or article.title
        summary = article.summary or article.translated_description or article.description
        full_text = article.translated_text or ""
        
        post = f"📢 *{title}*\n\n"
        
        if summary:
            post += f"{summary}\n\n"
        
        if full_text and len(full_text) > len(summary or ""):
            post += "---\n*Повний текст:*\n"
            if len(full_text) > 1000:
                post += f"{full_text[:997]}...\n\n"
            else:
                post += f"{full_text}\n\n"
        
        post += f"[Читати оригінал]({article.link})\n\n"
        post += f"Джерело: {article.source}"
        
        if article.detected_language:
            post += f" | Мова: {article.detected_language}"
        
        return post
    
    def run_full_workflow(self) -> dict:
        """
        Запускає повний workflow всіх кроків
        
        Returns:
            Словник з результатами
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_articles': 0,
            'ukraine_articles': 0,
            'translated_articles': 0,
            'saved_to_sheets': False,
            'published_to_telegram': 0,
            'errors': []
        }
        
        try:
            # КРОК 3: Парсинг
            all_articles = self.step_3_parse_news()
            results['total_articles'] = len(all_articles)
            
            if not all_articles:
                logger.info("Немає статей за сьогодні")
                return results
            
            # КРОК 4: Фільтрація
            ukraine_articles = self.step_4_filter_ukraine_news(all_articles)
            results['ukraine_articles'] = len(ukraine_articles)
            
            if not ukraine_articles:
                logger.info("Немає статей про Україну")
                return results
            
            # КРОК 5: Повний текст
            articles_with_text = self.step_5_fetch_full_text(ukraine_articles)
            
            # КРОК 6: Переклад
            translated_articles = self.step_6_translate_articles(articles_with_text)
            results['translated_articles'] = len(translated_articles)
            
            # КРОК 7: Синопсиси
            articles_with_summaries = self.step_7_create_summaries(translated_articles)
            
            # КРОК 8: Google Sheets
            sheets_success = self.step_8_save_to_google_sheets(articles_with_summaries)
            results['saved_to_sheets'] = sheets_success
            
            # КРОК 9: Telegram (тільки якщо не збережено в Sheets для модерації)
            if not sheets_success:
                published_count = self.step_9_publish_to_telegram(articles_with_summaries)
                results['published_to_telegram'] = published_count
            else:
                logger.info("Статті збережено в Google Sheets для модерації")
            
        except Exception as e:
            error_msg = f"Критична помилка в workflow: {e}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        
        return results


def main():
    """Основна функція"""
    # Налаштування логування
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('integrated_workflow.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    print("🇨🇭🇺🇦 Інтегрований парсер швейцарських новин про Україну")
    print("=" * 60)
    
    # Отримуємо API ключ
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        print("⚠️  OPENAI_API_KEY не налаштований")
        print("Деякі функції будуть недоступні")
    
    # Створюємо процесор
    processor = IntegratedNewsProcessor(openai_api_key)
    
    # Запускаємо повний workflow
    print("\n🚀 Запускаємо повний workflow...")
    results = processor.run_full_workflow()
    
    # Виводимо результати
    print("\n" + "="*60)
    print("📊 РЕЗУЛЬТАТИ WORKFLOW")
    print("="*60)
    print(f"📰 Всього статей за сьогодні: {results['total_articles']}")
    print(f"🇺🇦 Статей про Україну: {results['ukraine_articles']}")
    print(f"🔄 Перекладено статей: {results['translated_articles']}")
    print(f"📊 Збережено в Google Sheets: {'✅' if results['saved_to_sheets'] else '❌'}")
    print(f"📱 Опубліковано в Telegram: {results['published_to_telegram']}")
    
    if results['errors']:
        print(f"\n⚠️  Помилки ({len(results['errors'])}):")
        for error in results['errors']:
            print(f"   - {error}")
    
    print("="*60)
    
    # Зберігаємо результати
    import json
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"integrated_results_{timestamp}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Результати збережено: {results_file}")


if __name__ == "__main__":
    main()
