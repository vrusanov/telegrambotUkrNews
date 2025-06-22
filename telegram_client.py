"""
Telegram клієнт для надсилання повідомлень
Використовує python-telegram-bot з Markdown V2 форматуванням
"""

import logging
from typing import Optional, List
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError
import asyncio
import json
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class TelegramClient:
    """Клас для роботи з Telegram Bot API"""
    
    def __init__(self, token: str, channel_id: str):
        """
        Ініціалізація Telegram клієнта
        
        Args:
            token: Telegram Bot Token
            channel_id: ID каналу для публікації
        """
        self.bot = Bot(token=token)
        self.channel_id = channel_id
        self.seen_file = "data/seen.json"
        
        # Створюємо директорію для даних
        os.makedirs("data", exist_ok=True)
        
        # Завантажуємо список опублікованих URL
        self.seen_urls = self._load_seen_urls()
    
    def _load_seen_urls(self) -> set:
        """Завантажує список опублікованих URL"""
        try:
            if os.path.exists(self.seen_file):
                with open(self.seen_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('urls', []))
        except Exception as e:
            logger.warning(f"Не вдалося завантажити seen.json: {e}")
        
        return set()
    
    def _save_seen_urls(self):
        """Зберігає список опублікованих URL"""
        try:
            data = {
                'urls': list(self.seen_urls),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.seen_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Не вдалося зберегти seen.json: {e}")
    
    def _escape_markdown_v2(self, text: str) -> str:
        """Екранує спеціальні символи для Markdown V2"""
        if not text:
            return ""
        
        # Символи, які потрібно екранувати в Markdown V2
        escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        
        for char in escape_chars:
            text = text.replace(char, f'\\{char}')
        
        return text
    
    def _format_message(self, title: str, summary: str, full_text: str, url: str, source: str) -> str:
        """
        Форматує повідомлення в Markdown V2
        
        Args:
            title: Заголовок українською
            summary: Синопсис
            full_text: Повний текст
            url: Посилання на оригінал
            source: Джерело
            
        Returns:
            Відформатоване повідомлення
        """
        # Екранування тексту
        title_escaped = self._escape_markdown_v2(title)
        summary_escaped = self._escape_markdown_v2(summary)
        source_escaped = self._escape_markdown_v2(source)
        
        # Формуємо повідомлення
        message = f"📢 *{title_escaped}*\n\n"
        
        if summary:
            message += f"{summary_escaped}\n\n"
        
        if full_text and len(full_text) > len(summary or ""):
            message += "\\-\\-\\-\n*Повний текст:*\n"
            
            # Обмежуємо довжину повного тексту
            if len(full_text) > 1000:
                full_text_short = full_text[:997] + "..."
            else:
                full_text_short = full_text
            
            full_text_escaped = self._escape_markdown_v2(full_text_short)
            message += f"{full_text_escaped}\n\n"
        
        # Додаємо посилання
        message += f"[Читати оригінал]({url})\n\n"
        message += f"Джерело: {source_escaped}"
        
        return message
    
    def is_url_seen(self, url: str) -> bool:
        """Перевіряє, чи була стаття вже опублікована"""
        return url in self.seen_urls
    
    def mark_url_as_seen(self, url: str):
        """Позначає URL як опублікований"""
        self.seen_urls.add(url)
        self._save_seen_urls()
    
    async def send_message_async(self, title: str, summary: str, full_text: str, 
                                url: str, source: str) -> Optional[int]:
        """
        Асинхронно надсилає повідомлення в Telegram
        
        Args:
            title: Заголовок українською
            summary: Синопсис
            full_text: Повний текст
            url: Посилання на оригінал
            source: Джерело
            
        Returns:
            ID повідомлення або None у разі помилки
        """
        # Перевіряємо, чи не дублюємо
        if self.is_url_seen(url):
            logger.info(f"URL вже опублікований: {url}")
            return None
        
        try:
            # Форматуємо повідомлення
            message = self._format_message(title, summary, full_text, url, source)
            
            # Надсилаємо повідомлення
            sent_message = await self.bot.send_message(
                chat_id=self.channel_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=False
            )
            
            # Позначаємо як опублікований
            self.mark_url_as_seen(url)
            
            logger.info(f"Повідомлення надіслано: ID {sent_message.message_id}")
            return sent_message.message_id
            
        except TelegramError as e:
            logger.error(f"Помилка Telegram API: {e}")
            return None
        except Exception as e:
            logger.error(f"Помилка надсилання повідомлення: {e}")
            return None
    
    def send_message(self, title: str, summary: str, full_text: str, 
                    url: str, source: str) -> Optional[int]:
        """
        Синхронна обгортка для надсилання повідомлення
        
        Args:
            title: Заголовок українською
            summary: Синопсис
            full_text: Повний текст
            url: Посилання на оригінал
            source: Джерело
            
        Returns:
            ID повідомлення або None у разі помилки
        """
        try:
            # Запускаємо асинхронну функцію
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.send_message_async(title, summary, full_text, url, source)
            )
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Помилка синхронного виклику: {e}")
            return None
    
    async def test_connection_async(self) -> bool:
        """Асинхронно тестує з'єднання з Telegram"""
        try:
            me = await self.bot.get_me()
            logger.info(f"Telegram бот підключено: @{me.username}")
            return True
        except Exception as e:
            logger.error(f"Помилка підключення до Telegram: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Синхронна обгортка для тестування з'єднання"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.test_connection_async())
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Помилка тестування з'єднання: {e}")
            return False
    
    def send_multiple_messages(self, articles_data: List[dict]) -> List[Optional[int]]:
        """
        Надсилає кілька повідомлень
        
        Args:
            articles_data: Список словників з даними статей
            
        Returns:
            Список ID повідомлень
        """
        message_ids = []
        
        for article_data in articles_data:
            try:
                message_id = self.send_message(
                    title=article_data.get('title', ''),
                    summary=article_data.get('summary', ''),
                    full_text=article_data.get('full_text', ''),
                    url=article_data.get('url', ''),
                    source=article_data.get('source', '')
                )
                message_ids.append(message_id)
                
                # Затримка між повідомленнями
                import time
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Помилка надсилання статті: {e}")
                message_ids.append(None)
        
        return message_ids


def main():
    """Тестування Telegram клієнта"""
    import os
    
    token = os.getenv('TELEGRAM_TOKEN')
    channel_id = os.getenv('TELEGRAM_CHANNEL')
    
    if not token or not channel_id:
        print("Встановіть TELEGRAM_TOKEN та TELEGRAM_CHANNEL для тестування")
        return
    
    client = TelegramClient(token, channel_id)
    
    # Тест з'єднання
    if client.test_connection():
        print("✅ Telegram бот підключено успішно")
        
        # Тестове повідомлення
        test_data = {
            'title': 'Тестова новина про Україну',
            'summary': 'Це тестовий синопсис новини для перевірки роботи Telegram бота.',
            'full_text': 'Повний текст тестової новини з детальною інформацією про подію.',
            'url': 'https://example.com/test-article',
            'source': 'test'
        }
        
        message_id = client.send_message(**test_data)
        if message_id:
            print(f"✅ Тестове повідомлення надіслано: ID {message_id}")
        else:
            print("❌ Не вдалося надіслати тестове повідомлення")
    else:
        print("❌ Не вдалося підключитися до Telegram")


if __name__ == "__main__":
    main()
