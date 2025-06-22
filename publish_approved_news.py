"""
Скрипт для публікації схвалених новин з Google Sheets
Читає схвалені статті та публікує їх в Telegram з зображеннями
"""

import os
import logging
from typing import List, Dict
from datetime import datetime

from google_sheets_integration import GoogleSheetsManager
from dalle_image_generator import DALLEImageGenerator
from telegram_bot_advanced import TelegramBotAdvanced

logger = logging.getLogger(__name__)


class ApprovedNewsPublisher:
    """Клас для публікації схвалених новин"""
    
    def __init__(self, config: Dict[str, str]):
        """
        Ініціалізація публікатора
        
        Args:
            config: Конфігурація з API ключами та шляхами
        """
        self.config = config
        self.sheets_manager = None
        self.image_generator = None
        self.telegram_bot = None
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Ініціалізує компоненти"""
        try:
            # Google Sheets
            credentials_path = self.config.get('google_credentials_path')
            spreadsheet_id = self.config.get('google_spreadsheet_id')
            
            if credentials_path and spreadsheet_id and os.path.exists(credentials_path):
                self.sheets_manager = GoogleSheetsManager(credentials_path, spreadsheet_id)
                logger.info("Google Sheets підключено")
            else:
                raise ValueError("Google Sheets не налаштовано")
            
            # DALL-E (опціонально)
            openai_key = self.config.get('openai_api_key')
            if openai_key:
                images_dir = self.config.get('images_dir', 'images')
                self.image_generator = DALLEImageGenerator(openai_key, images_dir)
                logger.info("DALL-E генератор підключено")
            
            # Telegram
            bot_token = self.config.get('telegram_bot_token')
            chat_id = self.config.get('telegram_chat_id')
            
            if bot_token and chat_id:
                self.telegram_bot = TelegramBotAdvanced(bot_token, chat_id)
                logger.info("Telegram бот підключено")
            else:
                raise ValueError("Telegram не налаштовано")
                
        except Exception as e:
            logger.error(f"Помилка ініціалізації: {e}")
            raise
    
    def get_approved_articles(self) -> List[Dict]:
        """
        Отримує схвалені, але не опубліковані статті
        
        Returns:
            Список схвалених статей
        """
        if not self.sheets_manager:
            logger.error("Google Sheets не підключено")
            return []
        
        try:
            articles = self.sheets_manager.get_unpublished_approved_articles()
            logger.info(f"Знайдено {len(articles)} схвалених неопублікованих статей")
            return articles
        except Exception as e:
            logger.error(f"Помилка отримання схвалених статей: {e}")
            return []
    
    def generate_image_if_needed(self, article: Dict, row_number: int) -> str:
        """
        Генерує зображення для статті якщо потрібно
        
        Args:
            article: Дані статті
            row_number: Номер рядка в таблиці
            
        Returns:
            Шлях до зображення або None
        """
        if not self.image_generator:
            logger.info("DALL-E не налаштовано, пропускаємо генерацію зображення")
            return None
        
        # Перевіряємо чи вже згенеровано зображення
        image_generated = article.get('Image_Generated', '').lower()
        if image_generated in ['yes', 'так', 'y', '1']:
            logger.info("Зображення вже згенеровано для цієї статті")
            return None
        
        summary = article.get('Summary', '')
        if not summary:
            logger.warning("Немає синопсису для генерації зображення")
            return None
        
        try:
            logger.info("Генеруємо зображення для статті...")
            
            # Генеруємо ім'я файлу
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            title_safe = article.get('Title', 'article').replace(' ', '_')[:20]
            filename = f"{title_safe}_{timestamp}.png"
            
            # Генеруємо зображення
            image_path = self.image_generator.generate_and_save_image(summary, filename)
            
            if image_path:
                # Оновлюємо статус в Google Sheets
                self.sheets_manager.update_image_status(row_number, "Yes")
                logger.info(f"Зображення згенеровано: {image_path}")
                return image_path
            else:
                logger.error("Не вдалося згенерувати зображення")
                return None
                
        except Exception as e:
            logger.error(f"Помилка генерації зображення: {e}")
            return None
    
    def create_telegram_post(self, article: Dict) -> str:
        """
        Створює Telegram пост з даних статті
        
        Args:
            article: Дані статті з Google Sheets
            
        Returns:
            Готовий текст для Telegram
        """
        title = article.get('Title', 'Без заголовка')
        summary = article.get('Summary', '')
        full_text = article.get('FullText', '')
        link = article.get('Link', '')
        source = article.get('Source', '')
        
        # Створюємо пост
        post = f"📢 *{title}*\n\n"
        
        if summary:
            post += f"{summary}\n\n"
        
        if full_text and full_text != summary:
            post += "---\n*Повний текст:*\n"
            # Обмежуємо довжину повного тексту
            if len(full_text) > 1000:
                post += f"{full_text[:997]}...\n\n"
            else:
                post += f"{full_text}\n\n"
        
        if link:
            post += f"[Читати оригінал]({link})\n\n"
        
        if source:
            post += f"Джерело: {source}"
        
        return post
    
    def publish_article(self, article: Dict, row_number: int) -> bool:
        """
        Публікує одну статтю
        
        Args:
            article: Дані статті
            row_number: Номер рядка в Google Sheets
            
        Returns:
            True якщо успішно опубліковано
        """
        try:
            title = article.get('Title', 'Без заголовка')
            logger.info(f"Публікуємо статтю: {title}")
            
            # Генеруємо зображення якщо потрібно
            image_path = self.generate_image_if_needed(article, row_number)
            
            # Створюємо текст посту
            post_text = self.create_telegram_post(article)
            
            # Публікуємо в Telegram
            result = self.telegram_bot.send_post_with_image(post_text, image_path)
            
            if result.get("ok"):
                # Позначаємо як опубліковано в Google Sheets
                self.sheets_manager.mark_as_published(row_number)
                logger.info(f"Стаття успішно опублікована: {title}")
                return True
            else:
                logger.error(f"Не вдалося опублікувати статтю: {result.get('description')}")
                return False
                
        except Exception as e:
            logger.error(f"Помилка публікації статті: {e}")
            return False
    
    def publish_all_approved(self, max_articles: int = 10) -> Dict[str, int]:
        """
        Публікує всі схвалені статті
        
        Args:
            max_articles: Максимальна кількість статей для публікації
            
        Returns:
            Статистика публікації
        """
        results = {
            'total_found': 0,
            'published': 0,
            'failed': 0,
            'skipped': 0
        }
        
        try:
            # Отримуємо схвалені статті
            approved_articles = self.get_approved_articles()
            results['total_found'] = len(approved_articles)
            
            if not approved_articles:
                logger.info("Немає схвалених статей для публікації")
                return results
            
            # Обмежуємо кількість статей
            articles_to_publish = approved_articles[:max_articles]
            if len(approved_articles) > max_articles:
                results['skipped'] = len(approved_articles) - max_articles
                logger.info(f"Обмежуємо публікацію до {max_articles} статей")
            
            # Тестуємо Telegram з'єднання
            if not self.telegram_bot.test_connection():
                logger.error("Не вдалося підключитися до Telegram")
                results['failed'] = len(articles_to_publish)
                return results
            
            # Публікуємо статті
            for i, article in enumerate(articles_to_publish):
                try:
                    # Номер рядка в Google Sheets (починається з 2, бо 1 - заголовки)
                    row_number = i + 2  # Це спрощення, в реальності потрібно знати точний номер
                    
                    if self.publish_article(article, row_number):
                        results['published'] += 1
                    else:
                        results['failed'] += 1
                    
                    # Затримка між публікаціями
                    import time
                    time.sleep(3)
                    
                except Exception as e:
                    logger.error(f"Помилка публікації статті {i+1}: {e}")
                    results['failed'] += 1
            
            logger.info(f"Публікація завершена: {results}")
            
        except Exception as e:
            logger.error(f"Помилка в процесі публікації: {e}")
        
        return results


def main():
    """Основна функція для запуску публікації"""
    # Налаштування логування
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('publish_approved.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger.info("Запуск публікації схвалених новин")
    
    # Конфігурація
    config = {
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'google_credentials_path': os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json'),
        'google_spreadsheet_id': os.getenv('GOOGLE_SPREADSHEET_ID'),
        'telegram_bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
        'telegram_chat_id': os.getenv('TELEGRAM_CHAT_ID'),
        'images_dir': os.getenv('IMAGES_DIR', 'images')
    }
    
    # Перевіряємо обов'язкові параметри
    required_params = ['google_spreadsheet_id', 'telegram_bot_token', 'telegram_chat_id']
    missing_params = [param for param in required_params if not config.get(param)]
    
    if missing_params:
        logger.error(f"Відсутні обов'язкові параметри: {missing_params}")
        return
    
    try:
        # Створюємо публікатор
        publisher = ApprovedNewsPublisher(config)
        
        # Публікуємо схвалені статті
        results = publisher.publish_all_approved(max_articles=5)
        
        # Виводимо результати
        print("\n" + "="*50)
        print("РЕЗУЛЬТАТИ ПУБЛІКАЦІЇ")
        print("="*50)
        print(f"Знайдено схвалених статей: {results['total_found']}")
        print(f"Успішно опубліковано: {results['published']}")
        print(f"Помилки публікації: {results['failed']}")
        print(f"Пропущено (ліміт): {results['skipped']}")
        print("="*50)
        
    except Exception as e:
        logger.error(f"Критична помилка: {e}")


if __name__ == "__main__":
    main()
