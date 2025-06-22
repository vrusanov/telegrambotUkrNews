"""
Модуль для інтеграції з Telegram Bot API
Опціональний модуль для автоматичної відправки новин в Telegram
"""

import os
import requests
import logging
from typing import List, Optional
from rss_parser import NewsArticle

logger = logging.getLogger(__name__)


class TelegramBot:
    """Клас для роботи з Telegram Bot API"""
    
    def __init__(self, bot_token: str, chat_id: str):
        """
        Ініціалізація Telegram бота
        
        Args:
            bot_token: Токен Telegram бота
            chat_id: ID чату для відправки повідомлень
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """
        Відправляє повідомлення в Telegram
        
        Args:
            text: Текст повідомлення
            parse_mode: Режим парсингу (Markdown або HTML)
            
        Returns:
            True якщо повідомлення відправлено успішно
        """
        url = f"{self.base_url}/sendMessage"
        
        data = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": False
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get("ok"):
                logger.info("Повідомлення успішно відправлено в Telegram")
                return True
            else:
                logger.error(f"Помилка Telegram API: {result.get('description')}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Помилка при відправці в Telegram: {e}")
            return False
    
    def send_article(self, article: NewsArticle) -> bool:
        """
        Відправляє статтю в Telegram
        
        Args:
            article: Об'єкт статті
            
        Returns:
            True якщо повідомлення відправлено успішно
        """
        if article.telegram_post:
            return self.send_message(article.telegram_post)
        else:
            # Створюємо базове повідомлення якщо немає готового Telegram-посту
            message = f"""📢 *{article.translated_title or article.title}*

{article.summary or article.description}

[Читати повністю]({article.link})

Джерело: {article.source}"""
            
            return self.send_message(message)
    
    def send_articles_batch(self, articles: List[NewsArticle], 
                          max_articles: int = 5) -> int:
        """
        Відправляє кілька статей в Telegram
        
        Args:
            articles: Список статей
            max_articles: Максимальна кількість статей для відправки
            
        Returns:
            Кількість успішно відправлених статей
        """
        sent_count = 0
        
        # Обмежуємо кількість статей
        articles_to_send = articles[:max_articles]
        
        if len(articles_to_send) > 1:
            # Відправляємо заголовок якщо кілька статей
            header = f"🇺🇦 *Нові новини про Україну* ({len(articles_to_send)} статей)"
            self.send_message(header)
        
        for i, article in enumerate(articles_to_send, 1):
            try:
                if self.send_article(article):
                    sent_count += 1
                    logger.info(f"Відправлено статтю {i}/{len(articles_to_send)}: {article.title}")
                else:
                    logger.error(f"Не вдалося відправити статтю: {article.title}")
                    
                # Невелика затримка між повідомленнями
                import time
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Помилка при відправці статті {article.title}: {e}")
        
        return sent_count
    
    def test_connection(self) -> bool:
        """
        Тестує з'єднання з Telegram Bot API
        
        Returns:
            True якщо з'єднання працює
        """
        url = f"{self.base_url}/getMe"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get("ok"):
                bot_info = result.get("result", {})
                logger.info(f"Telegram бот підключено: @{bot_info.get('username')}")
                return True
            else:
                logger.error(f"Помилка Telegram API: {result.get('description')}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Помилка підключення до Telegram: {e}")
            return False


def send_news_to_telegram(articles: List[NewsArticle], 
                         bot_token: Optional[str] = None,
                         chat_id: Optional[str] = None) -> bool:
    """
    Відправляє новини в Telegram
    
    Args:
        articles: Список статей для відправки
        bot_token: Токен бота (якщо None, береться з змінних середовища)
        chat_id: ID чату (якщо None, береться з змінних середовища)
        
    Returns:
        True якщо хоча б одна стаття відправлена успішно
    """
    # Отримуємо параметри з змінних середовища якщо не передані
    if not bot_token:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not chat_id:
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        logger.warning("Telegram інтеграція не налаштована (немає токена або chat_id)")
        return False
    
    if not articles:
        logger.info("Немає статей для відправки в Telegram")
        return False
    
    try:
        bot = TelegramBot(bot_token, chat_id)
        
        # Тестуємо з'єднання
        if not bot.test_connection():
            return False
        
        # Відправляємо статті
        sent_count = bot.send_articles_batch(articles)
        
        if sent_count > 0:
            logger.info(f"Успішно відправлено {sent_count} статей в Telegram")
            return True
        else:
            logger.error("Не вдалося відправити жодної статті в Telegram")
            return False
            
    except Exception as e:
        logger.error(f"Помилка при відправці в Telegram: {e}")
        return False


# Приклад використання
if __name__ == "__main__":
    # Налаштування логування
    logging.basicConfig(level=logging.INFO)
    
    # Тестування Telegram інтеграції
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if bot_token and chat_id:
        bot = TelegramBot(bot_token, chat_id)
        
        # Тест з'єднання
        if bot.test_connection():
            # Тестове повідомлення
            test_message = "🧪 Тест Telegram інтеграції парсера швейцарських новин"
            bot.send_message(test_message)
        else:
            print("❌ Не вдалося підключитися до Telegram")
    else:
        print("⚠️ Налаштуйте TELEGRAM_BOT_TOKEN та TELEGRAM_CHAT_ID в змінних середовища")
