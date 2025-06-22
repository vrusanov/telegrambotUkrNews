"""
Модуль для інтеграції з Google Sheets API
Зберігає сформовані новини у Google таблицю для модерації
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
import gspread
from google.oauth2.service_account import Credentials
from rss_parser import NewsArticle

logger = logging.getLogger(__name__)


class GoogleSheetsManager:
    """Клас для роботи з Google Sheets API"""
    
    def __init__(self, credentials_path: str, spreadsheet_id: str):
        """
        Ініціалізація Google Sheets менеджера
        
        Args:
            credentials_path: Шлях до JSON файлу з credentials service account
            spreadsheet_id: ID Google таблиці
        """
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id
        self.client = None
        self.worksheet = None
        
        # Налаштування scope для Google Sheets API
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        self._authenticate()
    
    def _authenticate(self):
        """Аутентифікація з Google Sheets API"""
        try:
            if not os.path.exists(self.credentials_path):
                raise FileNotFoundError(f"Файл credentials не знайдено: {self.credentials_path}")
            
            # Завантажуємо credentials
            credentials = Credentials.from_service_account_file(
                self.credentials_path, 
                scopes=self.scope
            )
            
            # Створюємо клієнт
            self.client = gspread.authorize(credentials)
            
            # Відкриваємо таблицю
            spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            
            # Отримуємо або створюємо worksheet
            try:
                self.worksheet = spreadsheet.worksheet("News")
            except gspread.WorksheetNotFound:
                self.worksheet = spreadsheet.add_worksheet(title="News", rows=1000, cols=10)
                self._setup_headers()
            
            logger.info("Успішно підключено до Google Sheets")
            
        except Exception as e:
            logger.error(f"Помилка аутентифікації Google Sheets: {e}")
            raise
    
    def _setup_headers(self):
        """Налаштовує заголовки колонок у таблиці"""
        headers = [
            "Timestamp",
            "Source", 
            "Title",
            "Summary",
            "FullText",
            "Link",
            "Approved",
            "Published",
            "Notes",
            "Image_Generated"
        ]
        
        try:
            self.worksheet.update('A1:J1', [headers])
            
            # Форматування заголовків
            self.worksheet.format('A1:J1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
            })
            
            logger.info("Заголовки таблиці налаштовано")
            
        except Exception as e:
            logger.error(f"Помилка налаштування заголовків: {e}")
    
    def add_article(self, article: NewsArticle) -> bool:
        """
        Додає статтю до Google таблиці
        
        Args:
            article: Об'єкт новинної статті
            
        Returns:
            True якщо стаття успішно додана
        """
        try:
            if not self.worksheet:
                logger.error("Worksheet не ініціалізований")
                return False
            
            # Підготовка даних для додавання
            row_data = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Timestamp
                article.source,                                 # Source
                article.translated_title or article.title,     # Title
                article.summary or "",                          # Summary
                article.translated_text or article.description, # FullText
                article.link,                                   # Link
                "No",                                          # Approved (за замовчуванням)
                "No",                                          # Published
                "",                                            # Notes
                "No"                                           # Image_Generated
            ]
            
            # Додаємо рядок до таблиці
            self.worksheet.append_row(row_data)
            
            logger.info(f"Стаття додана до Google Sheets: {article.title}")
            return True
            
        except Exception as e:
            logger.error(f"Помилка додавання статті до Google Sheets: {e}")
            return False
    
    def add_articles_batch(self, articles: List[NewsArticle]) -> int:
        """
        Додає кілька статей до таблиці
        
        Args:
            articles: Список статей
            
        Returns:
            Кількість успішно доданих статей
        """
        added_count = 0
        
        for article in articles:
            if self.add_article(article):
                added_count += 1
        
        logger.info(f"Додано {added_count} з {len(articles)} статей до Google Sheets")
        return added_count
    
    def get_approved_articles(self) -> List[Dict]:
        """
        Отримує список схвалених статей з таблиці
        
        Returns:
            Список словників з даними статей
        """
        try:
            if not self.worksheet:
                logger.error("Worksheet не ініціалізований")
                return []
            
            # Отримуємо всі записи
            records = self.worksheet.get_all_records()
            
            # Фільтруємо схвалені статті
            approved_articles = [
                record for record in records 
                if record.get('Approved', '').lower() in ['yes', 'так', 'y', '1']
            ]
            
            logger.info(f"Знайдено {len(approved_articles)} схвалених статей")
            return approved_articles
            
        except Exception as e:
            logger.error(f"Помилка отримання схвалених статей: {e}")
            return []
    
    def mark_as_published(self, row_number: int) -> bool:
        """
        Позначає статтю як опубліковану
        
        Args:
            row_number: Номер рядка в таблиці (починаючи з 1)
            
        Returns:
            True якщо успішно позначено
        """
        try:
            if not self.worksheet:
                logger.error("Worksheet не ініціалізований")
                return False
            
            # Позначаємо як опубліковано (колонка H - Published)
            self.worksheet.update_cell(row_number, 8, "Yes")
            
            logger.info(f"Стаття в рядку {row_number} позначена як опублікована")
            return True
            
        except Exception as e:
            logger.error(f"Помилка позначення як опублікована: {e}")
            return False
    
    def update_image_status(self, row_number: int, status: str = "Yes") -> bool:
        """
        Оновлює статус генерації зображення
        
        Args:
            row_number: Номер рядка в таблиці
            status: Статус генерації зображення
            
        Returns:
            True якщо успішно оновлено
        """
        try:
            if not self.worksheet:
                logger.error("Worksheet не ініціалізований")
                return False
            
            # Оновлюємо статус зображення (колонка J - Image_Generated)
            self.worksheet.update_cell(row_number, 10, status)
            
            logger.info(f"Статус зображення оновлено для рядка {row_number}")
            return True
            
        except Exception as e:
            logger.error(f"Помилка оновлення статусу зображення: {e}")
            return False
    
    def get_unpublished_approved_articles(self) -> List[Dict]:
        """
        Отримує схвалені, але ще не опубліковані статті
        
        Returns:
            Список словників з даними статей
        """
        try:
            records = self.worksheet.get_all_records()
            
            unpublished_approved = [
                record for record in records 
                if (record.get('Approved', '').lower() in ['yes', 'так', 'y', '1'] and
                    record.get('Published', '').lower() not in ['yes', 'так', 'y', '1'])
            ]
            
            logger.info(f"Знайдено {len(unpublished_approved)} неопублікованих схвалених статей")
            return unpublished_approved
            
        except Exception as e:
            logger.error(f"Помилка отримання неопублікованих статей: {e}")
            return []


def save_articles_to_sheets(articles: List[NewsArticle], 
                          credentials_path: Optional[str] = None,
                          spreadsheet_id: Optional[str] = None) -> bool:
    """
    Зберігає статті у Google Sheets
    
    Args:
        articles: Список статей для збереження
        credentials_path: Шлях до credentials файлу
        spreadsheet_id: ID Google таблиці
        
    Returns:
        True якщо статті успішно збережено
    """
    # Отримуємо параметри з змінних середовища якщо не передані
    if not credentials_path:
        credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
    if not spreadsheet_id:
        spreadsheet_id = os.getenv('GOOGLE_SPREADSHEET_ID')
    
    if not spreadsheet_id:
        logger.warning("Google Sheets інтеграція не налаштована (немає spreadsheet_id)")
        return False
    
    if not os.path.exists(credentials_path):
        logger.warning(f"Файл credentials не знайдено: {credentials_path}")
        return False
    
    if not articles:
        logger.info("Немає статей для збереження в Google Sheets")
        return False
    
    try:
        sheets_manager = GoogleSheetsManager(credentials_path, spreadsheet_id)
        added_count = sheets_manager.add_articles_batch(articles)
        
        if added_count > 0:
            logger.info(f"Успішно збережено {added_count} статей у Google Sheets")
            return True
        else:
            logger.error("Не вдалося зберегти жодної статті у Google Sheets")
            return False
            
    except Exception as e:
        logger.error(f"Помилка збереження у Google Sheets: {e}")
        return False


# Приклад використання
if __name__ == "__main__":
    # Налаштування логування
    logging.basicConfig(level=logging.INFO)
    
    # Тестування Google Sheets інтеграції
    credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
    spreadsheet_id = os.getenv('GOOGLE_SPREADSHEET_ID')
    
    if credentials_path and spreadsheet_id and os.path.exists(credentials_path):
        try:
            sheets_manager = GoogleSheetsManager(credentials_path, spreadsheet_id)
            
            # Тестове додавання статті
            from datetime import datetime
            import pytz
            
            test_article = NewsArticle(
                title="Test Article",
                description="Test description",
                link="https://example.com",
                source="test",
                published_date=datetime.now(pytz.UTC)
            )
            test_article.translated_title = "Тестова стаття"
            test_article.summary = "Тестовий синопсис"
            test_article.translated_text = "Тестовий переклад"
            
            success = sheets_manager.add_article(test_article)
            if success:
                print("✅ Тестова стаття успішно додана до Google Sheets")
            else:
                print("❌ Не вдалося додати тестову статтю")
                
        except Exception as e:
            print(f"❌ Помилка тестування Google Sheets: {e}")
    else:
        print("⚠️ Налаштуйте GOOGLE_CREDENTIALS_PATH та GOOGLE_SPREADSHEET_ID")
