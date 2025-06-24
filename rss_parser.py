"""
Основний модуль для парсингу RSS-стрічок швейцарських новинних сайтів
"""

import feedparser
import requests
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import pytz
from typing import List, Dict, Optional
import logging
import re
from bs4 import BeautifulSoup

from config import RSS_FEEDS, UKRAINE_KEYWORDS
from gpt_processor import GPTProcessor

logger = logging.getLogger(__name__)


class NewsArticle:
    """Клас для представлення новинної статті"""
    
    def __init__(self, title: str, description: str, link: str, 
                 source: str, published_date: datetime):
        self.title = title
        self.description = description
        self.link = link
        self.source = source
        self.published_date = published_date
        self.is_ukraine_related = False
        self.translated_title = None
        self.translated_text = None
        self.summary = None
        self.telegram_post = None
    
    def __str__(self):
        return f"{self.source}: {self.title} ({self.published_date})"


class SwissNewsParser:
    """Парсер швейцарських новинних RSS-стрічок"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Ініціалізація парсера
        
        Args:
            openai_api_key: API ключ для OpenAI (опціонально)
        """
        self.gpt_processor = GPTProcessor(openai_api_key) if openai_api_key else None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _clean_text(self, text: str) -> str:
        """Очищає текст від HTML тегів та зайвих символів"""
        if not text:
            return ""
        
        # Видаляємо HTML теги
        soup = BeautifulSoup(text, 'html.parser')
        clean_text = soup.get_text()
        
        # Очищаємо від зайвих пробілів
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text
    
    def _parse_date(self, date_string: str) -> Optional[datetime]:
        """Парсить дату з RSS"""
        try:
            parsed_date = date_parser.parse(date_string)
            # Конвертуємо в UTC якщо немає timezone
            if parsed_date.tzinfo is None:
                parsed_date = pytz.UTC.localize(parsed_date)
            return parsed_date
        except Exception as e:
            logger.warning(f"Не вдалося розпарсити дату: {date_string}, помилка: {e}")
            return None
    
    def _is_recent(self, published_date: datetime, hours: int = 24) -> bool:
        """Перевіряє, чи була стаття опублікована за останні N годин"""
        if not published_date:
            return False
        
        now = datetime.now(pytz.UTC)
        time_threshold = now - timedelta(hours=hours)
        return published_date >= time_threshold
    
    def _contains_ukraine_keywords(self, text: str) -> bool:
        """Перевіряє, чи містить текст ключові слова про Україну"""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in UKRAINE_KEYWORDS)
    
    def _fetch_full_article_text(self, url: str) -> str:
        """Намагається отримати повний текст статті з веб-сторінки"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Видаляємо скрипти та стилі
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Шукаємо основний контент (різні селектори для різних сайтів)
            content_selectors = [
                'article', '.article-content', '.content', '.post-content',
                '.entry-content', 'main', '.main-content'
            ]
            
            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = elements[0].get_text()
                    break
            
            if not content:
                content = soup.get_text()
            
            return self._clean_text(content)
            
        except Exception as e:
            logger.warning(f"Не вдалося отримати повний текст з {url}: {e}")
            return ""
    
    def parse_rss_feed(self, feed_url: str, source_name: str) -> List[NewsArticle]:
        """
        Парсить одну RSS-стрічку
        
        Args:
            feed_url: URL RSS-стрічки
            source_name: Назва джерела
            
        Returns:
            Список статей
        """
        articles = []
        
        try:
            logger.info(f"Парсимо RSS з {source_name}: {feed_url}")
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                logger.warning(f"RSS стрічка {source_name} має помилки парсингу")
            
            for entry in feed.entries:
                # Отримуємо дату публікації
                published_date = None
                if hasattr(entry, 'published'):
                    published_date = self._parse_date(entry.published)
                elif hasattr(entry, 'updated'):
                    published_date = self._parse_date(entry.updated)
                
                # Пропускаємо статті без дати або старіші за 24 години
                if not published_date or not self._is_recent(published_date):
                    continue
                
                # Створюємо об'єкт статті
                title = self._clean_text(getattr(entry, 'title', ''))
                description = self._clean_text(getattr(entry, 'summary', ''))
                link = getattr(entry, 'link', '')
                
                if not title or not link:
                    continue
                
                article = NewsArticle(
                    title=title,
                    description=description,
                    link=link,
                    source=source_name,
                    published_date=published_date
                )
                
                articles.append(article)
                
        except Exception as e:
            logger.error(f"Помилка при парсингу RSS {source_name}: {e}")
        
        return articles

    def filter_ukraine_related(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """
        Фільтрує статті, пов'язані з Україною

        Args:
            articles: Список всіх статей

        Returns:
            Список статей про Україну
        """
        ukraine_articles = []

        for article in articles:
            # Перевіряємо ключові слова в заголовку та описі
            text_to_check = f"{article.title} {article.description}"

            if self._contains_ukraine_keywords(text_to_check):
                article.is_ukraine_related = True
                ukraine_articles.append(article)
                logger.info(f"Знайдено статтю про Україну: {article.title}")
            elif self.gpt_processor:
                # Додаткова перевірка через GPT
                classification = self.gpt_processor.classify_news(text_to_check)
                if classification == "Ukraine-related":
                    article.is_ukraine_related = True
                    ukraine_articles.append(article)
                    logger.info(f"GPT визначив як статтю про Україну: {article.title}")

        return ukraine_articles

    def process_ukraine_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """
        Обробляє статті про Україну: перекладає, створює резюме та Telegram-пости

        Args:
            articles: Список статей про Україну

        Returns:
            Оброблені статті
        """
        if not self.gpt_processor:
            logger.warning("GPT процесор не ініціалізований, пропускаємо обробку")
            return articles

        processed_articles = []

        for article in articles:
            logger.info(f"Обробляємо статтю: {article.title}")

            # Отримуємо повний текст статті
            full_text = self._fetch_full_article_text(article.link)
            if not full_text:
                full_text = article.description

            # Перекладаємо заголовок
            translated_title = self.gpt_processor.translate_to_ukrainian(article.title)
            if translated_title:
                article.translated_title = translated_title

            # Перекладаємо повний текст
            translated_text = self.gpt_processor.translate_to_ukrainian(full_text)
            if translated_text:
                article.translated_text = translated_text

                # Створюємо резюме
                summary = self.gpt_processor.create_summary(translated_text)
                if summary:
                    article.summary = summary

                    # Генеруємо Telegram-пост
                    telegram_post = self.gpt_processor.generate_telegram_post(
                        title=article.translated_title or article.title,
                        summary=summary,
                        full_text=translated_text,
                        source_url=article.link
                    )
                    if telegram_post:
                        article.telegram_post = telegram_post

            processed_articles.append(article)

        return processed_articles

    def parse_all_feeds(self, hours_back: int = 24) -> Dict[str, List[NewsArticle]]:
        """
        Парсить всі RSS-стрічки

        Args:
            hours_back: Скільки годин назад шукати новини

        Returns:
            Словник з результатами парсингу
        """
        all_articles = []
        results = {
            'all_articles': [],
            'ukraine_articles': [],
            'processed_articles': []
        }

        # Парсимо всі RSS-стрічки
        for source_name, feed_url in RSS_FEEDS.items():
            articles = self.parse_rss_feed(feed_url, source_name)
            all_articles.extend(articles)

        results['all_articles'] = all_articles
        logger.info(f"Знайдено {len(all_articles)} статей за останні {hours_back} годин")

        # Фільтруємо статті про Україну
        ukraine_articles = self.filter_ukraine_related(all_articles)
        results['ukraine_articles'] = ukraine_articles
        logger.info(f"З них {len(ukraine_articles)} статей про Україну")

        # Обробляємо статті про Україну
        if ukraine_articles:
            processed_articles = self.process_ukraine_articles(ukraine_articles)
            results['processed_articles'] = processed_articles
            logger.info(f"Оброблено {len(processed_articles)} статей")

        return results
