"""
Розширений модуль для роботи з Telegram Bot API
Підтримує відправку повідомлень з зображеннями та без них
"""

import os
import requests
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class TelegramBotAdvanced:
    """Розширений клас для роботи з Telegram Bot API"""
    
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
    
    def send_message(self, text: str, parse_mode: str = "Markdown", 
                    disable_web_page_preview: bool = False) -> Dict[str, Any]:
        """
        Відправляє текстове повідомлення
        
        Args:
            text: Текст повідомлення
            parse_mode: Режим парсингу (Markdown або HTML)
            disable_web_page_preview: Вимкнути попередній перегляд посилань
            
        Returns:
            Відповідь від Telegram API
        """
        url = f"{self.base_url}/sendMessage"
        
        data = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview
        }
        
        try:
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if result.get("ok"):
                logger.info("Текстове повідомлення успішно відправлено")
                return result
            else:
                logger.error(f"Помилка Telegram API: {result.get('description')}")
                return result
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Помилка при відправці повідомлення: {e}")
            return {"ok": False, "error": str(e)}
    
    def send_photo(self, image_path: str, caption: str = "", 
                  parse_mode: str = "Markdown") -> Dict[str, Any]:
        """
        Відправляє фото з підписом
        
        Args:
            image_path: Шлях до файлу зображення
            caption: Підпис до фото
            parse_mode: Режим парсингу підпису
            
        Returns:
            Відповідь від Telegram API
        """
        url = f"{self.base_url}/sendPhoto"
        
        # Перевіряємо існування файлу
        if not os.path.exists(image_path):
            logger.error(f"Файл зображення не знайдено: {image_path}")
            return {"ok": False, "error": "File not found"}
        
        # Перевіряємо розмір файлу (Telegram ліміт 50MB)
        file_size = os.path.getsize(image_path)
        if file_size > 50 * 1024 * 1024:  # 50MB
            logger.error(f"Файл занадто великий: {file_size} bytes")
            return {"ok": False, "error": "File too large"}
        
        data = {
            "chat_id": self.chat_id,
            "caption": caption,
            "parse_mode": parse_mode
        }
        
        try:
            with open(image_path, 'rb') as photo_file:
                files = {"photo": photo_file}
                response = requests.post(url, data=data, files=files, timeout=60)
                response.raise_for_status()
            
            result = response.json()
            if result.get("ok"):
                logger.info(f"Фото успішно відправлено: {image_path}")
                return result
            else:
                logger.error(f"Помилка Telegram API: {result.get('description')}")
                return result
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Помилка при відправці фото: {e}")
            return {"ok": False, "error": str(e)}
        except IOError as e:
            logger.error(f"Помилка читання файлу: {e}")
            return {"ok": False, "error": str(e)}
    
    def send_post_with_image(self, text: str, image_path: Optional[str] = None,
                           parse_mode: str = "Markdown") -> Dict[str, Any]:
        """
        Відправляє пост з текстом і зображенням (якщо є)
        
        Args:
            text: Текст повідомлення
            image_path: Шлях до зображення (опціонально)
            parse_mode: Режим парсингу
            
        Returns:
            Відповідь від Telegram API
        """
        if image_path and os.path.exists(image_path):
            # Відправляємо фото з підписом
            return self.send_photo(image_path, caption=text, parse_mode=parse_mode)
        else:
            # Відправляємо тільки текст
            if image_path:
                logger.warning(f"Зображення не знайдено: {image_path}, відправляємо тільки текст")
            return self.send_message(text, parse_mode=parse_mode)
    
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


def publish_to_telegram(text: str, image_path: Optional[str] = None,
                       bot_token: Optional[str] = None, 
                       chat_id: Optional[str] = None) -> bool:
    """
    Публікує повідомлення в Telegram з текстом і зображенням
    
    Args:
        text: Текст повідомлення
        image_path: Шлях до зображення (опціонально)
        bot_token: Токен бота (якщо None, береться з змінних середовища)
        chat_id: ID чату (якщо None, береться з змінних середовища)
        
    Returns:
        True якщо повідомлення успішно відправлено
    """
    # Отримуємо параметри з змінних середовища якщо не передані
    if not bot_token:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not chat_id:
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        logger.error("Telegram параметри не налаштовані (TOKEN або CHAT_ID)")
        return False
    
    if not text.strip():
        logger.error("Текст повідомлення порожній")
        return False
    
    try:
        bot = TelegramBotAdvanced(bot_token, chat_id)
        
        # Тестуємо з'єднання
        if not bot.test_connection():
            return False
        
        # Відправляємо повідомлення
        result = bot.send_post_with_image(text, image_path)
        
        if result.get("ok"):
            logger.info("Повідомлення успішно опубліковано в Telegram")
            return True
        else:
            logger.error(f"Не вдалося опублікувати в Telegram: {result.get('description', 'Unknown error')}")
            return False
            
    except Exception as e:
        logger.error(f"Помилка публікації в Telegram: {e}")
        return False


def send_news_batch_with_images(news_data: list, images_dir: str = "images",
                              bot_token: Optional[str] = None,
                              chat_id: Optional[str] = None) -> int:
    """
    Відправляє кілька новин з зображеннями
    
    Args:
        news_data: Список словників з даними новин
        images_dir: Директорія з зображеннями
        bot_token: Токен бота
        chat_id: ID чату
        
    Returns:
        Кількість успішно відправлених повідомлень
    """
    if not bot_token:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not chat_id:
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        logger.error("Telegram параметри не налаштовані")
        return 0
    
    bot = TelegramBotAdvanced(bot_token, chat_id)
    
    if not bot.test_connection():
        return 0
    
    sent_count = 0
    
    for i, news_item in enumerate(news_data):
        try:
            text = news_item.get('text', '')
            title = news_item.get('title', f'News {i+1}')
            
            if not text:
                logger.warning(f"Пропускаємо новину без тексту: {title}")
                continue
            
            # Шукаємо відповідне зображення
            image_path = None
            if images_dir and os.path.exists(images_dir):
                # Можливі імена файлів зображень
                possible_names = [
                    f"news_{i+1}.jpg",
                    f"news_{i+1}.png", 
                    f"{title.lower().replace(' ', '_')}.jpg",
                    f"{title.lower().replace(' ', '_')}.png"
                ]
                
                for name in possible_names:
                    full_path = os.path.join(images_dir, name)
                    if os.path.exists(full_path):
                        image_path = full_path
                        break
            
            # Відправляємо повідомлення
            result = bot.send_post_with_image(text, image_path)
            
            if result.get("ok"):
                sent_count += 1
                logger.info(f"Відправлено новину {i+1}/{len(news_data)}: {title}")
            else:
                logger.error(f"Не вдалося відправити новину: {title}")
            
            # Затримка між повідомленнями
            import time
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Помилка відправки новини {i+1}: {e}")
    
    logger.info(f"Успішно відправлено {sent_count} з {len(news_data)} новин")
    return sent_count


# Приклад використання
if __name__ == "__main__":
    # Налаштування логування
    logging.basicConfig(level=logging.INFO)
    
    # Тестування Telegram бота
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if bot_token and chat_id:
        # Тест з'єднання
        bot = TelegramBotAdvanced(bot_token, chat_id)
        
        if bot.test_connection():
            # Тестове повідомлення
            test_text = """🧪 *Тест розширеного Telegram бота*

Це тестове повідомлення для перевірки функціональності розширеного Telegram бота.

✅ Підтримка Markdown
📷 Підтримка зображень
🔗 [Посилання](https://example.com)"""
            
            result = bot.send_message(test_text)
            
            if result.get("ok"):
                print("✅ Тестове повідомлення успішно відправлено")
            else:
                print(f"❌ Помилка відправки: {result.get('description')}")
        else:
            print("❌ Не вдалося підключитися до Telegram")
    else:
        print("⚠️ Налаштуйте TELEGRAM_BOT_TOKEN та TELEGRAM_CHAT_ID")
