"""
Тестовий скрипт для перевірки функціональності парсера
"""

import os
import sys
from datetime import datetime, timedelta
import pytz

from rss_parser import SwissNewsParser, NewsArticle
from gpt_processor import GPTProcessor
from config import RSS_FEEDS, UKRAINE_KEYWORDS


def test_rss_parsing():
    """Тестує базовий парсинг RSS без GPT"""
    print("🧪 Тестування базового парсингу RSS...")
    
    parser = SwissNewsParser()
    
    for source_name, feed_url in RSS_FEEDS.items():
        print(f"\n📡 Тестуємо {source_name}: {feed_url}")
        
        try:
            articles = parser.parse_rss_feed(feed_url, source_name)
            print(f"   ✅ Знайдено {len(articles)} статей за останні 24 години")
            
            if articles:
                latest = articles[0]
                print(f"   📰 Остання стаття: {latest.title[:60]}...")
                print(f"   🕒 Дата: {latest.published_date}")
        
        except Exception as e:
            print(f"   ❌ Помилка: {e}")


def test_ukraine_filtering():
    """Тестує фільтрацію новин про Україну"""
    print("\n🇺🇦 Тестування фільтрації новин про Україну...")
    
    # Створюємо тестові статті
    test_articles = [
        NewsArticle(
            title="Ukraine receives new military aid package",
            description="The latest aid package includes advanced weapons systems",
            link="https://example.com/1",
            source="test",
            published_date=datetime.now(pytz.UTC)
        ),
        NewsArticle(
            title="Swiss economy shows growth",
            description="GDP increased by 2.5% this quarter",
            link="https://example.com/2", 
            source="test",
            published_date=datetime.now(pytz.UTC)
        ),
        NewsArticle(
            title="Зеленський відвідав Швейцарію",
            description="Президент України провів переговори з швейцарськими лідерами",
            link="https://example.com/3",
            source="test", 
            published_date=datetime.now(pytz.UTC)
        )
    ]
    
    parser = SwissNewsParser()
    ukraine_articles = parser.filter_ukraine_related(test_articles)
    
    print(f"   📊 З {len(test_articles)} тестових статей, {len(ukraine_articles)} про Україну")
    
    for article in ukraine_articles:
        print(f"   ✅ Знайдено: {article.title}")


def test_gpt_integration():
    """Тестує інтеграцію з GPT"""
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("\n⚠️  Пропускаємо тест GPT - немає API ключа")
        return
    
    print("\n🤖 Тестування інтеграції з GPT...")
    
    try:
        gpt = GPTProcessor(api_key)
        
        # Тест класифікації
        test_text = "Ukraine receives humanitarian aid from Switzerland"
        classification = gpt.classify_news(test_text)
        print(f"   🔍 Класифікація '{test_text[:30]}...': {classification}")
        
        # Тест перекладу
        test_translation = gpt.translate_to_ukrainian("Switzerland provides aid to Ukraine")
        if test_translation:
            print(f"   🌐 Переклад: {test_translation[:60]}...")
        
        # Тест резюме
        test_summary = gpt.create_summary("Швейцарія надала гуманітарну допомогу Україні в розмірі 50 мільйонів франків")
        if test_summary:
            print(f"   📝 Резюме: {test_summary[:60]}...")
            
        print("   ✅ GPT інтеграція працює")
        
    except Exception as e:
        print(f"   ❌ Помилка GPT: {e}")


def test_keyword_detection():
    """Тестує виявлення ключових слів"""
    print("\n🔍 Тестування виявлення ключових слів...")
    
    test_texts = [
        "Ukraine war continues in eastern regions",
        "Ukrainer in der Schweiz finden Unterstützung", 
        "Les Ukrainiens reçoivent de l'aide humanitaire",
        "Зеленський провів переговори",
        "Swiss chocolate exports increase",
        "Kyiv mayor announces new initiatives"
    ]
    
    parser = SwissNewsParser()
    
    for text in test_texts:
        contains_keywords = parser._contains_ukraine_keywords(text)
        status = "✅" if contains_keywords else "❌"
        print(f"   {status} '{text}' - {contains_keywords}")


def test_date_parsing():
    """Тестує парсинг дат"""
    print("\n📅 Тестування парсингу дат...")
    
    test_dates = [
        "Wed, 22 Jun 2025 10:30:00 GMT",
        "2025-06-22T10:30:00Z",
        "2025-06-22T10:30:00+02:00",
        "Jun 22, 2025 10:30 AM"
    ]
    
    parser = SwissNewsParser()
    
    for date_str in test_dates:
        try:
            parsed_date = parser._parse_date(date_str)
            is_recent = parser._is_recent(parsed_date) if parsed_date else False
            print(f"   ✅ '{date_str}' -> {parsed_date} (recent: {is_recent})")
        except Exception as e:
            print(f"   ❌ '{date_str}' -> Помилка: {e}")


def main():
    """Запускає всі тести"""
    print("🧪 ТЕСТУВАННЯ ПАРСЕРА ШВЕЙЦАРСЬКИХ НОВИН")
    print("=" * 60)
    
    # Базові тести
    test_date_parsing()
    test_keyword_detection()
    test_ukraine_filtering()
    
    # Тести з мережею
    test_rss_parsing()
    
    # Тести GPT (якщо є API ключ)
    test_gpt_integration()
    
    print("\n" + "=" * 60)
    print("🏁 Тестування завершено")


if __name__ == "__main__":
    main()
