"""
Спеціалізований скрипт для парсингу новин з визначенням мови
Реалізує кроки 3-5 з технічного завдання
"""

import feedparser
import requests
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import pytz
from typing import List, Dict, Optional
import logging
from bs4 import BeautifulSoup
import re

# Додаємо визначення мови
try:
    from langdetect import detect, DetectorFactory
    # Встановлюємо seed для стабільних результатів
    DetectorFactory.seed = 0
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    logging.warning("langdetect не встановлено. Визначення мови недоступне.")

from config import RSS_FEEDS, UKRAINE_KEYWORDS

logger = logging.getLogger(__name__)


class NewsArticleWithLang:
    """Розширена модель новинної статті з визначенням мови"""
    
    def __init__(self, title: str, description: str, link: str, 
                 source: str, published_date: datetime):
        self.title = title
        self.description = description
        self.link = link
        self.source = source
        self.published_date = published_date
        
        # Додаткові поля
        self.detected_language = None
        self.full_text = None
        self.is_ukraine_related = False
        self.gpt_classification = None
        
        # Автоматично визначаємо мову
        self._detect_language()
    
    def _detect_language(self):
        """Визначає мову статті"""
        if not LANGDETECT_AVAILABLE:
            return
        
        try:
            # Об'єднуємо заголовок та опис для кращого визначення
            text_for_detection = f"{self.title} {self.description}"
            
            if len(text_for_detection.strip()) > 10:
                self.detected_language = detect(text_for_detection)
                logger.debug(f"Визначено мову: {self.detected_language} для статті: {self.title[:50]}...")
            else:
                logger.warning("Недостатньо тексту для визначення мови")
                
        except Exception as e:
            logger.warning(f"Помилка визначення мови: {e}")
            self.detected_language = "unknown"
    
    def __str__(self):
        lang_info = f" [{self.detected_language}]" if self.detected_language else ""
        return f"{self.source}{lang_info}: {self.title} ({self.published_date})"


class SwissNewsParser:
    """Парсер швейцарських новин з визначенням мови"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
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
    
    def _is_today(self, published_date: datetime) -> bool:
        """Перевіряє, чи була стаття опублікована сьогодні"""
        if not published_date:
            return False
        
        today = datetime.now(pytz.UTC).date()
        article_date = published_date.date()
        return article_date == today
    
    def _contains_ukraine_keywords(self, text: str) -> bool:
        """Перевіряє, чи містить текст ключові слова про Україну"""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in UKRAINE_KEYWORDS)
    
    def fetch_article_text(self, url: str) -> str:
        """
        Витягує повний текст статті з веб-сторінки
        
        Args:
            url: URL статті
            
        Returns:
            Повний текст статті
        """
        try:
            logger.info(f"Отримуємо повний текст з: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Видаляємо скрипти та стилі
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            
            # Специфічні селектори для різних сайтів
            content_selectors = {
                'swissinfo.ch': [
                    '.article__content',
                    '.article-content', 
                    '[data-testid="article-content"]',
                    '.content-main'
                ],
                'letemps.ch': [
                    '.article-content',
                    '.article__content',
                    '.content-article',
                    '.article-body'
                ],
                '20min.ch': [
                    '.article-content',
                    '.ArticleDetail_content',
                    '.content'
                ]
            }
            
            # Визначаємо сайт з URL
            site_key = None
            for key in content_selectors.keys():
                if key in url:
                    site_key = key
                    break
            
            content = ""
            
            # Пробуємо специфічні селектори для сайту
            if site_key and site_key in content_selectors:
                for selector in content_selectors[site_key]:
                    elements = soup.select(selector)
                    if elements:
                        content = elements[0].get_text()
                        break
            
            # Якщо не знайшли специфічний контент, пробуємо загальні селектори
            if not content:
                general_selectors = [
                    'article', '.article', '.post-content', '.entry-content',
                    '.content', '.main-content', 'main', '.article-body'
                ]
                
                for selector in general_selectors:
                    elements = soup.select(selector)
                    if elements:
                        content = elements[0].get_text()
                        break
            
            # Якщо все ще не знайшли, беремо весь текст
            if not content:
                content = soup.get_text()
            
            # Очищаємо текст
            clean_content = self._clean_text(content)
            
            # Перевіряємо мінімальну довжину
            if len(clean_content) < 100:
                logger.warning(f"Отримано занадто короткий текст з {url}")
                return ""
            
            logger.info(f"Отримано текст довжиною {len(clean_content)} символів")
            return clean_content
            
        except Exception as e:
            logger.error(f"Помилка отримання тексту з {url}: {e}")
            return ""
    
    def parse_rss_feed(self, feed_url: str, source_name: str) -> List[NewsArticleWithLang]:
        """
        Парсить одну RSS-стрічку та повертає новини за сьогодні
        
        Args:
            feed_url: URL RSS-стрічки
            source_name: Назва джерела
            
        Returns:
            Список статей за сьогодні
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
                
                # Пропускаємо статті не за сьогодні
                if not published_date or not self._is_today(published_date):
                    continue
                
                # Створюємо об'єкт статті
                title = self._clean_text(getattr(entry, 'title', ''))
                description = self._clean_text(getattr(entry, 'summary', ''))
                link = getattr(entry, 'link', '')
                
                if not title or not link:
                    continue
                
                article = NewsArticleWithLang(
                    title=title,
                    description=description,
                    link=link,
                    source=source_name,
                    published_date=published_date
                )
                
                # Перевіряємо ключові слова
                text_to_check = f"{article.title} {article.description}"
                if self._contains_ukraine_keywords(text_to_check):
                    article.is_ukraine_related = True
                    logger.info(f"Знайдено статтю про Україну: {article.title}")
                
                articles.append(article)
                
        except Exception as e:
            logger.error(f"Помилка при парсингу RSS {source_name}: {e}")
        
        return articles
    
    def parse_all_feeds_today(self) -> Dict[str, List[NewsArticleWithLang]]:
        """
        Парсить всі RSS-стрічки та повертає новини за сьогодні
        
        Returns:
            Словник з результатами парсингу
        """
        all_articles = []
        ukraine_articles = []
        
        # Парсимо всі RSS-стрічки
        for source_name, feed_url in RSS_FEEDS.items():
            articles = self.parse_rss_feed(feed_url, source_name)
            all_articles.extend(articles)
            
            # Фільтруємо статті про Україну
            for article in articles:
                if article.is_ukraine_related:
                    ukraine_articles.append(article)
        
        results = {
            'all_articles': all_articles,
            'ukraine_articles': ukraine_articles,
            'total_count': len(all_articles),
            'ukraine_count': len(ukraine_articles)
        }
        
        logger.info(f"Знайдено {len(all_articles)} статей за сьогодні")
        logger.info(f"З них {len(ukraine_articles)} статей про Україну")
        
        return results
    
    def get_articles_with_full_text(self, articles: List[NewsArticleWithLang]) -> List[NewsArticleWithLang]:
        """
        Отримує повний текст для списку статей
        
        Args:
            articles: Список статей
            
        Returns:
            Список статей з повним текстом
        """
        for article in articles:
            try:
                logger.info(f"Отримуємо повний текст для: {article.title}")
                article.full_text = self.fetch_article_text(article.link)
                
                # Невелика затримка між запитами
                import time
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Помилка отримання тексту для {article.title}: {e}")
        
        return articles


def classify_with_gpt(article: NewsArticleWithLang, gpt_processor=None) -> str:
    """
    Класифікує новину через GPT
    
    Args:
        article: Стаття для класифікації
        gpt_processor: GPT процесор (опціонально)
        
    Returns:
        "Ukraine-related" або "Not related"
    """
    if not gpt_processor:
        logger.warning("GPT процесор не надано, пропускаємо класифікацію")
        return "Not classified"
    
    try:
        text_for_classification = f"{article.title}\n\n{article.description}"
        if article.full_text:
            # Використовуємо перші 500 символів повного тексту
            text_for_classification += f"\n\n{article.full_text[:500]}..."
        
        classification = gpt_processor.classify_news(text_for_classification)
        article.gpt_classification = classification
        
        logger.info(f"GPT класифікація для '{article.title}': {classification}")
        return classification
        
    except Exception as e:
        logger.error(f"Помилка GPT класифікації: {e}")
        return "Error"


def main():
    """Основна функція для тестування парсера"""
    # Налаштування логування
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("📰 Парсер швейцарських новин за сьогодні")
    print("=" * 50)
    
    # Перевіряємо доступність визначення мови
    if not LANGDETECT_AVAILABLE:
        print("⚠️  langdetect не встановлено. Встановіть: pip install langdetect")
    
    # Створюємо парсер
    parser = SwissNewsParser()
    
    # Парсимо новини за сьогодні
    results = parser.parse_all_feeds_today()
    
    print(f"\n📊 Результати парсингу:")
    print(f"   Всього статей за сьогодні: {results['total_count']}")
    print(f"   Статей про Україну: {results['ukraine_count']}")
    
    # Виводимо всі статті
    if results['all_articles']:
        print(f"\n📋 Всі статті за сьогодні:")
        for i, article in enumerate(results['all_articles'], 1):
            ukraine_mark = "🇺🇦" if article.is_ukraine_related else "  "
            print(f"{i:2d}. {ukraine_mark} {article}")
    
    # Детально виводимо статті про Україну
    if results['ukraine_articles']:
        print(f"\n🇺🇦 Статті про Україну:")
        for i, article in enumerate(results['ukraine_articles'], 1):
            print(f"\n{i}. {article.source.upper()}")
            print(f"   Заголовок: {article.title}")
            print(f"   Мова: {article.detected_language or 'невизначено'}")
            print(f"   Опис: {article.description[:200]}...")
            print(f"   Посилання: {article.link}")
            print(f"   Дата: {article.published_date}")
        
        # Отримуємо повний текст для статей про Україну
        print(f"\n📄 Отримуємо повний текст статей...")
        ukraine_with_text = parser.get_articles_with_full_text(results['ukraine_articles'])
        
        for article in ukraine_with_text:
            if article.full_text:
                print(f"\n📰 Повний текст: {article.title}")
                print(f"Довжина: {len(article.full_text)} символів")
                print(f"Початок: {article.full_text[:300]}...")
    else:
        print("\n🔍 Статей про Україну за сьогодні не знайдено")


if __name__ == "__main__":
    main()
