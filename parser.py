"""
RSS/HTML парсер згідно з технічними вимогами
Використовує feedparser + BeautifulSoup для fallback HTML-парсингу
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import pytz
from typing import List, Dict, Optional
import logging
from langdetect import detect, DetectorFactory
import re

# Встановлюємо seed для стабільних результатів
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)

# RSS стрічки
RSS_FEEDS = {
    'swissinfo': 'https://www.swissinfo.ch/rss',
    '20min': 'https://www.20min.ch/rss',
    'letemps': 'https://www.letemps.ch/rss',
    'nzz': 'https://www.nzz.ch/recent.rss'
}

# Ключові слова для фільтрації
UKRAINE_KEYWORDS = [
    "Україна", "українці", "Ukraine", "Ukrainer", "Ukrainiens",
    "Kyiv", "Kiev", "Zelensky", "Zelenskyy", "Зеленський"
]


class Article:
    """Модель новинної статті"""
    
    def __init__(self, title: str, description: str, url: str, 
                 source: str, published_date: datetime):
        self.title = title
        self.description = description
        self.url = url
        self.source = source
        self.published_date = published_date
        self.language = None
        self.full_text = None
        self.is_ukraine_related = False
        
        # Автоматично визначаємо мову
        self._detect_language()
    
    def _detect_language(self):
        """Визначає мову статті через langdetect"""
        try:
            text_for_detection = f"{self.title} {self.description}"
            if len(text_for_detection.strip()) > 10:
                self.language = detect(text_for_detection)
                logger.debug(f"Визначено мову: {self.language} для {self.title[:50]}...")
        except Exception as e:
            logger.warning(f"Помилка визначення мови: {e}")
            self.language = "unknown"
    
    def __str__(self):
        return f"{self.source} [{self.language}]: {self.title}"


class NewsParser:
    """RSS/HTML парсер новин"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _clean_text(self, text: str) -> str:
        """Очищає текст від HTML тегів"""
        if not text:
            return ""
        soup = BeautifulSoup(text, 'html.parser')
        clean_text = soup.get_text()
        return re.sub(r'\s+', ' ', clean_text).strip()
    
    def _parse_date(self, date_string: str) -> Optional[datetime]:
        """Парсить дату з RSS"""
        try:
            parsed_date = date_parser.parse(date_string)
            if parsed_date.tzinfo is None:
                parsed_date = pytz.UTC.localize(parsed_date)
            return parsed_date
        except Exception as e:
            logger.warning(f"Не вдалося розпарсити дату: {date_string}")
            return None
    
    def _is_recent(self, published_date: datetime, hours: int = 24) -> bool:
        """Перевіряє, чи стаття опублікована за останні N годин"""
        if not published_date:
            return False
        now = datetime.now(pytz.UTC)
        return published_date >= (now - timedelta(hours=hours))
    
    def _contains_ukraine_keywords(self, text: str) -> bool:
        """Перевіряє наявність ключових слів про Україну"""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in UKRAINE_KEYWORDS)
    
    def parse_rss_feed(self, feed_url: str, source_name: str) -> List[Article]:
        """Парсить RSS стрічку через feedparser"""
        articles = []
        
        try:
            logger.info(f"Парсимо RSS: {source_name}")
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                logger.warning(f"RSS стрічка {source_name} має помилки")
            
            for entry in feed.entries:
                # Парсимо дату
                published_date = None
                if hasattr(entry, 'published'):
                    published_date = self._parse_date(entry.published)
                elif hasattr(entry, 'updated'):
                    published_date = self._parse_date(entry.updated)
                
                # Фільтруємо за часом (останні 24 години)
                if not published_date or not self._is_recent(published_date):
                    continue
                
                # Створюємо статтю
                title = self._clean_text(getattr(entry, 'title', ''))
                description = self._clean_text(getattr(entry, 'summary', ''))
                url = getattr(entry, 'link', '')
                
                if not title or not url:
                    continue
                
                article = Article(title, description, url, source_name, published_date)
                
                # Перевіряємо ключові слова
                text_to_check = f"{article.title} {article.description}"
                if self._contains_ukraine_keywords(text_to_check):
                    article.is_ukraine_related = True
                    logger.info(f"Знайдено статтю про Україну: {article.title}")
                
                articles.append(article)
                
        except Exception as e:
            logger.error(f"Помилка парсингу RSS {source_name}: {e}")
        
        return articles
    
    def fetch_full_text(self, article: Article) -> str:
        """Завантажує повний текст статті через BeautifulSoup"""
        try:
            logger.info(f"Завантажуємо повний текст: {article.url}")
            response = self.session.get(article.url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Видаляємо непотрібні елементи
            for element in soup(['script', 'style', 'nav', 'header', 'footer']):
                element.decompose()
            
            # Селектори для різних сайтів
            selectors = {
                'swissinfo.ch': ['.article__content', '[data-testid="article-content"]'],
                'letemps.ch': ['.article-content', '.article__content'],
                '20min.ch': ['.article-content', '.ArticleDetail_content'],
                'nzz.ch': ['.articlecomponent', '.article-content']
            }
            
            content = ""
            site_key = None
            
            # Визначаємо сайт
            for key in selectors.keys():
                if key in article.url:
                    site_key = key
                    break
            
            # Пробуємо специфічні селектори
            if site_key:
                for selector in selectors[site_key]:
                    elements = soup.select(selector)
                    if elements:
                        content = elements[0].get_text()
                        break
            
            # Fallback до загальних селекторів
            if not content:
                for selector in ['article', '.article', '.content', 'main']:
                    elements = soup.select(selector)
                    if elements:
                        content = elements[0].get_text()
                        break
            
            # Останній fallback - весь текст
            if not content:
                content = soup.get_text()
            
            clean_content = self._clean_text(content)
            
            if len(clean_content) < 100:
                logger.warning(f"Занадто короткий текст з {article.url}")
                return ""
            
            article.full_text = clean_content
            logger.info(f"Отримано {len(clean_content)} символів")
            return clean_content
            
        except Exception as e:
            logger.error(f"Помилка завантаження тексту з {article.url}: {e}")
            return ""
    
    def parse_all_feeds(self) -> List[Article]:
        """Парсить всі RSS стрічки"""
        all_articles = []
        
        for source_name, feed_url in RSS_FEEDS.items():
            articles = self.parse_rss_feed(feed_url, source_name)
            all_articles.extend(articles)
        
        logger.info(f"Знайдено {len(all_articles)} статей за останні 24 години")
        
        # Фільтруємо статті про Україну
        ukraine_articles = [a for a in all_articles if a.is_ukraine_related]
        logger.info(f"З них {len(ukraine_articles)} про Україну")
        
        return ukraine_articles
    
    def get_articles_with_full_text(self, articles: List[Article]) -> List[Article]:
        """Завантажує повний текст для списку статей"""
        for article in articles:
            self.fetch_full_text(article)
            # Затримка між запитами
            import time
            time.sleep(1)
        
        return articles


def main():
    """Тестування парсера"""
    logging.basicConfig(level=logging.INFO)
    
    parser = NewsParser()
    articles = parser.parse_all_feeds()
    
    print(f"Знайдено {len(articles)} статей про Україну:")
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article}")
    
    if articles:
        print("\nЗавантажуємо повний текст...")
        articles_with_text = parser.get_articles_with_full_text(articles)
        
        for article in articles_with_text:
            if article.full_text:
                print(f"\n{article.title}")
                print(f"Текст: {len(article.full_text)} символів")


if __name__ == "__main__":
    main()
