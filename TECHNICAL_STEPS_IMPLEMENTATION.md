# Реалізація технічних кроків парсера новин

## ✅ Статус виконання всіх кроків

| Крок | Опис | Файл | Статус |
|------|------|------|--------|
| 3 | Парсинг RSS з визначенням мови | `parse_news.py` | ✅ Виконано |
| 4 | Фільтр за ключовими словами + GPT | `parse_news.py` | ✅ Виконано |
| 5 | Отримання повного тексту статті | `parse_news.py` | ✅ Виконано |
| 6 | Переклад з урахуванням мови | `translation_service.py` | ✅ Виконано |
| 7 | Генерація синопсису | `translation_service.py` | ✅ Виконано |
| 8 | Збереження в Google Sheets | `google_sheets_integration.py` | ✅ Виконано |
| 9 | Публікація в Telegram | `telegram_bot_advanced.py` | ✅ Виконано |
| 10 | Автоматизація (GitHub Actions) | `.github/workflows/daily-news-parser.yml` | ✅ Виконано |

---

## 🔹 КРОК 3: Парсинг новин з визначенням мови

### Файл: `parse_news.py`

**Функціональність:**
- Парсинг RSS з https://www.swissinfo.ch/rss та https://www.letemps.ch/rss
- Фільтрація новин за сьогоднішню дату
- Автоматичне визначення мови через `langdetect`
- Структурований вивід: заголовок, опис, посилання, джерело, мова

**Ключові класи:**
```python
class NewsArticleWithLang:
    def __init__(self, title, description, link, source, published_date):
        self.detected_language = None  # Автоматично визначається
        self._detect_language()

class SwissNewsParser:
    def parse_all_feeds_today(self) -> Dict[str, List[NewsArticleWithLang]]
```

**Приклад використання:**
```bash
python parse_news.py
```

**Вивід:**
```
📰 Парсер швейцарських новин за сьогодні
📊 Результати парсингу:
   Всього статей за сьогодні: 15
   Статей про Україну: 3

📋 Всі статті за сьогодні:
 1. 🇺🇦 swissinfo [de]: Schweiz unterstützt Ukraine...
 2.    20min [fr]: Nouvelles mesures économiques...
```

---

## 🔹 КРОК 4: Фільтр за ключовими словами + GPT

### Файл: `parse_news.py` (функція `classify_with_gpt`)

**Функціональність:**
- Перевірка ключових слів: "Україна", "українці", "Ukraine", "Ukrainer", "Ukrainiens"
- Додаткова GPT класифікація для сумнівних випадків
- Повернення: "Ukraine-related" або "Not related"

**Ключові слова (з config.py):**
```python
UKRAINE_KEYWORDS = [
    "Україна", "українці", "Ukraine", "Ukrainer", "Ukrainiens",
    "Kyiv", "Kiev", "Zelensky", "Zelenskyy", "Зеленський"
]
```

**GPT промпт:**
```
Проаналізуй наступний текст новини та визнач, чи стосується він України або українців.
Відповідь має бути лише "Ukraine-related" або "Not related".
```

---

## 🔹 КРОК 5: Отримання повного тексту статті

### Файл: `parse_news.py` (метод `fetch_article_text`)

**Функціональність:**
- Завантаження HTML сторінки статті
- Витягування основного контенту через BeautifulSoup
- Специфічні селектори для різних сайтів
- Очищення від HTML тегів та зайвих елементів

**Селектори для сайтів:**
```python
content_selectors = {
    'swissinfo.ch': ['.article__content', '[data-testid="article-content"]'],
    'letemps.ch': ['.article-content', '.article__content'],
    '20min.ch': ['.article-content', '.ArticleDetail_content']
}
```

**Приклад:**
```python
parser = SwissNewsParser()
full_text = parser.fetch_article_text("https://www.swissinfo.ch/article/...")
print(f"Отримано {len(full_text)} символів")
```

---

## 🔹 КРОК 6: Переклад з урахуванням мови

### Файл: `translation_service.py`

**Функціональність:**
- Автоматичний вибір промпту залежно від мови оригіналу
- Підтримка німецької, французької, італійської, англійської
- Збереження офіційного новинного стилю

**Промпти для різних мов:**
```python
translation_prompts = {
    'de': "Переклади з німецької на українську...",
    'fr': "Переклади з французької на українську...",
    'en': "Переклади з англійської на українську...",
    'default': "Автоматично визнач мову та переклади..."
}
```

**Приклад використання:**
```python
translator = TranslationService(api_key)
translation = translator.translate_to_ukrainian(
    text="Die Schweiz unterstützt die Ukraine",
    source_lang="de"
)
```

---

## 🔹 КРОК 7: Генерація синопсису

### Файл: `translation_service.py` (метод `summarize_article`)

**Функціональність:**
- Створення короткого синопсису 3-5 речень
- Включення ключових елементів: хто, що, де/коли, чому важливо
- Використання перекладеного тексту

**GPT промпт:**
```
Сформулюй короткий синопсис цієї новини українською мовою, 3–5 речень. 
Включи: хто, що, де/коли, чому важливо.
```

**Приклад:**
```python
summary = translator.summarize_article(translated_text)
# Результат: "Швейцарський уряд оголосив про надання 50 млн франків..."
```

---

## 🔹 КРОК 8: Збереження в Google Sheets

### Файл: `google_sheets_integration.py`

**Функціональність:**
- Автоматичне створення таблиці з заголовками
- Поля: Title, Summary, FullText, Link, Approved (Yes/No)
- Service Account аутентифікація
- Workflow модерації

**Структура таблиці:**
| Timestamp | Source | Title | Summary | FullText | Link | Approved | Published | Notes | Image_Generated |

**Приклад використання:**
```python
from google_sheets_integration import save_articles_to_sheets

success = save_articles_to_sheets(processed_articles)
if success:
    print("✅ Статті збережено для модерації")
```

**Налаштування:**
1. Створити Google Cloud проект
2. Увімкнути Google Sheets API
3. Створити Service Account
4. Завантажити credentials.json
5. Надати доступ до таблиці

---

## 🔹 КРОК 9: Публікація в Telegram

### Файл: `telegram_bot_advanced.py`

**Функціональність:**
- Підтримка sendPhoto та sendMessage
- Автоматичний вибір методу залежно від наявності зображення
- Форматування Markdown
- Обробка помилок та retry логіка

**Формат повідомлення:**
```
📢 *Заголовок українською*

Синопсис новини (3-5 речень)

---
*Повний текст:*
Перекладений текст новини...

[Читати оригінал](посилання)
Джерело: swissinfo
```

**Приклад використання:**
```python
from telegram_bot_advanced import publish_to_telegram

success = publish_to_telegram(
    text="📢 *Новина*\n\nТекст...",
    image_path="images/news_image.png"
)
```

---

## 🔹 КРОК 10: Автоматизація через GitHub Actions

### Файл: `.github/workflows/daily-news-parser.yml`

**Функціональність:**
- Щоденний запуск о 07:00 UTC
- Можливість ручного запуску з параметрами
- Два job'и: парсинг + публікація після модерації
- Сповіщення в Telegram про результати

**Розклад:**
```yaml
schedule:
  - cron: '0 7 * * *'  # Щодня о 07:00 UTC
```

**Секрети для налаштування:**
- `OPENAI_API_KEY`
- `GOOGLE_CREDENTIALS_JSON`
- `GOOGLE_SPREADSHEET_ID`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

**Workflow:**
1. **Job 1**: Парсинг → Обробка → Збереження в Google Sheets
2. **Пауза**: 3 години для модерації
3. **Job 2**: Публікація схвалених статей

---

## 🚀 Інтегрований запуск всіх кроків

### Файл: `integrated_main.py`

**Повний workflow:**
```python
processor = IntegratedNewsProcessor(openai_api_key)
results = processor.run_full_workflow()
```

**Кроки виконання:**
1. ✅ Парсинг RSS з визначенням мови
2. ✅ Фільтрація за ключовими словами + GPT
3. ✅ Отримання повного тексту
4. ✅ Переклад з урахуванням мови оригіналу
5. ✅ Створення синопсисів
6. ✅ Збереження в Google Sheets
7. ✅ Публікація в Telegram (або очікування модерації)

**Запуск:**
```bash
python integrated_main.py
```

**Результат:**
```
📊 РЕЗУЛЬТАТИ WORKFLOW
📰 Всього статей за сьогодні: 15
🇺🇦 Статей про Україну: 3
🔄 Перекладено статей: 3
📊 Збережено в Google Sheets: ✅
📱 Опубліковано в Telegram: 0 (очікує модерації)
```

---

## 📋 Налаштування та запуск

### 1. Встановлення залежностей
```bash
pip install -r requirements.txt
```

### 2. Налаштування змінних середовища
```bash
export OPENAI_API_KEY="your-key"
export GOOGLE_SPREADSHEET_ID="your-id"
export TELEGRAM_BOT_TOKEN="your-token"
export TELEGRAM_CHAT_ID="your-chat-id"
```

### 3. Налаштування Google Sheets
Дотримуйтесь інструкцій в `GOOGLE_SHEETS_SETUP.md`

### 4. Запуск
```bash
# Тестування окремих кроків
python parse_news.py
python translation_service.py

# Повний workflow
python integrated_main.py

# Або використовуйте основний скрипт
python main.py
```

### 5. Автоматизація
- Налаштуйте GitHub Actions секрети
- Workflow запуститься автоматично щодня
- Або запустіть вручну через GitHub interface

---

## 🎯 Всі кроки технічного завдання виконано!

✅ **КРОК 3**: Парсинг RSS з визначенням мови  
✅ **КРОК 4**: Фільтр за ключовими словами + GPT класифікація  
✅ **КРОК 5**: Отримання повного тексту статті  
✅ **КРОК 6**: Переклад з урахуванням мови оригіналу  
✅ **КРОК 7**: Генерація синопсису  
✅ **КРОК 8**: Збереження в Google Sheets з модерацією  
✅ **КРОК 9**: Публікація в Telegram з зображеннями  
✅ **КРОК 10**: Автоматизація через GitHub Actions  

**Бонус функції:**
- 🖼️ DALL-E генерація зображень
- 📊 Розширена Google Sheets інтеграція
- 🤖 Розширений Telegram бот
- 🔄 Інтегрований workflow менеджер
