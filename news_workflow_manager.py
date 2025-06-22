"""
Інтегрований модуль для управління повним workflow новин
Об'єднує парсинг, обробку GPT, збереження в Google Sheets, генерацію зображень та публікацію в Telegram
"""

import os
import logging
from typing import List, Dict, Optional
from datetime import datetime

from rss_parser import SwissNewsParser, NewsArticle
from google_sheets_integration import GoogleSheetsManager, save_articles_to_sheets
from dalle_image_generator import DALLEImageGenerator, generate_image_for_news
from telegram_bot_advanced import TelegramBotAdvanced, publish_to_telegram

logger = logging.getLogger(__name__)


class NewsWorkflowManager:
    """Менеджер для управління повним циклом обробки новин"""
    
    def __init__(self, config: Dict[str, str]):
        """
        Ініціалізація менеджера workflow
        
        Args:
            config: Словник з конфігурацією (API ключі, ID, шляхи)
        """
        self.config = config
        
        # Ініціалізуємо компоненти
        self.news_parser = None
        self.sheets_manager = None
        self.image_generator = None
        self.telegram_bot = None
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Ініціалізує всі компоненти системи"""
        try:
            # Парсер новин
            openai_key = self.config.get('openai_api_key')
            if openai_key:
                self.news_parser = SwissNewsParser(openai_key)
                logger.info("Парсер новин ініціалізовано з GPT підтримкою")
            else:
                self.news_parser = SwissNewsParser()
                logger.warning("Парсер новин ініціалізовано без GPT підтримки")
            
            # Google Sheets
            credentials_path = self.config.get('google_credentials_path')
            spreadsheet_id = self.config.get('google_spreadsheet_id')
            if credentials_path and spreadsheet_id and os.path.exists(credentials_path):
                self.sheets_manager = GoogleSheetsManager(credentials_path, spreadsheet_id)
                logger.info("Google Sheets менеджер ініціалізовано")
            else:
                logger.warning("Google Sheets не налаштовано")
            
            # DALL-E генератор зображень
            if openai_key:
                images_dir = self.config.get('images_dir', 'images')
                self.image_generator = DALLEImageGenerator(openai_key, images_dir)
                logger.info("DALL-E генератор ініціалізовано")
            else:
                logger.warning("DALL-E генератор не налаштовано")
            
            # Telegram бот
            bot_token = self.config.get('telegram_bot_token')
            chat_id = self.config.get('telegram_chat_id')
            if bot_token and chat_id:
                self.telegram_bot = TelegramBotAdvanced(bot_token, chat_id)
                logger.info("Telegram бот ініціалізовано")
            else:
                logger.warning("Telegram бот не налаштовано")
                
        except Exception as e:
            logger.error(f"Помилка ініціалізації компонентів: {e}")
    
    def parse_and_process_news(self, hours_back: int = 24) -> Dict[str, List]:
        """
        Парсить та обробляє новини
        
        Args:
            hours_back: Скільки годин назад шукати новини
            
        Returns:
            Словник з результатами обробки
        """
        logger.info("Починаємо парсинг та обробку новин...")
        
        if not self.news_parser:
            logger.error("Парсер новин не ініціалізований")
            return {}
        
        # Парсимо новини
        results = self.news_parser.parse_all_feeds(hours_back)
        
        logger.info(f"Парсинг завершено: {len(results.get('ukraine_articles', []))} статей про Україну")
        return results
    
    def save_to_sheets(self, articles: List[NewsArticle]) -> bool:
        """
        Зберігає статті в Google Sheets
        
        Args:
            articles: Список статей для збереження
            
        Returns:
            True якщо успішно збережено
        """
        if not self.sheets_manager:
            logger.warning("Google Sheets не налаштовано, пропускаємо збереження")
            return False
        
        if not articles:
            logger.info("Немає статей для збереження в Google Sheets")
            return True
        
        try:
            added_count = self.sheets_manager.add_articles_batch(articles)
            logger.info(f"Збережено {added_count} статей в Google Sheets")
            return added_count > 0
        except Exception as e:
            logger.error(f"Помилка збереження в Google Sheets: {e}")
            return False
    
    def generate_images_for_articles(self, articles: List[NewsArticle]) -> Dict[str, str]:
        """
        Генерує зображення для статей
        
        Args:
            articles: Список статей
            
        Returns:
            Словник {індекс: шлях_до_зображення}
        """
        if not self.image_generator:
            logger.warning("DALL-E генератор не налаштовано, пропускаємо генерацію зображень")
            return {}
        
        if not articles:
            logger.info("Немає статей для генерації зображень")
            return {}
        
        logger.info(f"Генеруємо зображення для {len(articles)} статей...")
        
        generated_images = {}
        
        for i, article in enumerate(articles):
            try:
                if not article.summary:
                    logger.warning(f"Пропускаємо статтю без синопсису: {article.title}")
                    continue
                
                logger.info(f"Генеруємо зображення для статті {i+1}: {article.title}")
                
                # Генеруємо ім'я файлу
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"news_{i+1}_{timestamp}.png"
                
                # Генеруємо зображення
                image_path = self.image_generator.generate_and_save_image(
                    article.summary, filename
                )
                
                if image_path:
                    generated_images[str(i)] = image_path
                    logger.info(f"Зображення згенеровано: {image_path}")
                else:
                    logger.error(f"Не вдалося згенерувати зображення для статті {i+1}")
                
                # Затримка між запитами
                import time
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"Помилка генерації зображення для статті {i+1}: {e}")
        
        logger.info(f"Згенеровано {len(generated_images)} зображень")
        return generated_images
    
    def publish_to_telegram(self, articles: List[NewsArticle], 
                          images: Dict[str, str] = None) -> int:
        """
        Публікує статті в Telegram
        
        Args:
            articles: Список статей
            images: Словник з шляхами до зображень
            
        Returns:
            Кількість успішно опублікованих статей
        """
        if not self.telegram_bot:
            logger.warning("Telegram бот не налаштовано, пропускаємо публікацію")
            return 0
        
        if not articles:
            logger.info("Немає статей для публікації в Telegram")
            return 0
        
        if not self.telegram_bot.test_connection():
            logger.error("Не вдалося підключитися до Telegram")
            return 0
        
        logger.info(f"Публікуємо {len(articles)} статей в Telegram...")
        
        published_count = 0
        images = images or {}
        
        for i, article in enumerate(articles):
            try:
                if not article.telegram_post:
                    logger.warning(f"Пропускаємо статтю без Telegram посту: {article.title}")
                    continue
                
                # Отримуємо шлях до зображення якщо є
                image_path = images.get(str(i))
                
                logger.info(f"Публікуємо статтю {i+1}: {article.title}")
                
                # Публікуємо в Telegram
                result = self.telegram_bot.send_post_with_image(
                    article.telegram_post, image_path
                )
                
                if result.get("ok"):
                    published_count += 1
                    logger.info(f"Стаття {i+1} успішно опублікована")
                else:
                    logger.error(f"Не вдалося опублікувати статтю {i+1}")
                
                # Затримка між публікаціями
                import time
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Помилка публікації статті {i+1}: {e}")
        
        logger.info(f"Опубліковано {published_count} з {len(articles)} статей")
        return published_count
    
    def run_full_workflow(self, hours_back: int = 24, 
                         generate_images: bool = True,
                         publish_immediately: bool = False) -> Dict[str, any]:
        """
        Запускає повний цикл обробки новин
        
        Args:
            hours_back: Скільки годин назад шукати новини
            generate_images: Чи генерувати зображення
            publish_immediately: Чи публікувати одразу (без модерації)
            
        Returns:
            Словник з результатами workflow
        """
        workflow_results = {
            'timestamp': datetime.now().isoformat(),
            'parsed_articles': 0,
            'ukraine_articles': 0,
            'processed_articles': 0,
            'saved_to_sheets': 0,
            'generated_images': 0,
            'published_to_telegram': 0,
            'errors': []
        }
        
        try:
            # 1. Парсинг та обробка новин
            logger.info("=== КРОК 1: Парсинг новин ===")
            parse_results = self.parse_and_process_news(hours_back)
            
            workflow_results['parsed_articles'] = len(parse_results.get('all_articles', []))
            workflow_results['ukraine_articles'] = len(parse_results.get('ukraine_articles', []))
            workflow_results['processed_articles'] = len(parse_results.get('processed_articles', []))
            
            processed_articles = parse_results.get('processed_articles', [])
            
            if not processed_articles:
                logger.info("Немає оброблених статей для подальшої роботи")
                return workflow_results
            
            # 2. Збереження в Google Sheets
            logger.info("=== КРОК 2: Збереження в Google Sheets ===")
            if self.save_to_sheets(processed_articles):
                workflow_results['saved_to_sheets'] = len(processed_articles)
            
            # 3. Генерація зображень
            generated_images = {}
            if generate_images:
                logger.info("=== КРОК 3: Генерація зображень ===")
                generated_images = self.generate_images_for_articles(processed_articles)
                workflow_results['generated_images'] = len(generated_images)
            
            # 4. Публікація в Telegram (якщо дозволено)
            if publish_immediately:
                logger.info("=== КРОК 4: Публікація в Telegram ===")
                published_count = self.publish_to_telegram(processed_articles, generated_images)
                workflow_results['published_to_telegram'] = published_count
            else:
                logger.info("Публікація в Telegram пропущена (потрібна модерація)")
            
            logger.info("=== WORKFLOW ЗАВЕРШЕНО ===")
            logger.info(f"Результати: {workflow_results}")
            
        except Exception as e:
            error_msg = f"Помилка в workflow: {e}"
            logger.error(error_msg)
            workflow_results['errors'].append(error_msg)
        
        return workflow_results


def create_workflow_config() -> Dict[str, str]:
    """
    Створює конфігурацію workflow з змінних середовища
    
    Returns:
        Словник з конфігурацією
    """
    return {
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'google_credentials_path': os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json'),
        'google_spreadsheet_id': os.getenv('GOOGLE_SPREADSHEET_ID'),
        'telegram_bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
        'telegram_chat_id': os.getenv('TELEGRAM_CHAT_ID'),
        'images_dir': os.getenv('IMAGES_DIR', 'images')
    }


# Приклад використання
if __name__ == "__main__":
    # Налаштування логування
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Створюємо конфігурацію
    config = create_workflow_config()
    
    # Створюємо менеджер workflow
    workflow_manager = NewsWorkflowManager(config)
    
    # Запускаємо повний цикл
    results = workflow_manager.run_full_workflow(
        hours_back=24,
        generate_images=True,
        publish_immediately=False  # Потрібна модерація через Google Sheets
    )
    
    print("\n" + "="*60)
    print("РЕЗУЛЬТАТИ WORKFLOW")
    print("="*60)
    for key, value in results.items():
        print(f"{key}: {value}")
    print("="*60)
