"""
Конфігураційний файл для парсера швейцарських новин
"""

# RSS стрічки швейцарських новинних сайтів
RSS_FEEDS = {
    'swissinfo': 'https://www.swissinfo.ch/rss',
    '20min': 'https://www.20min.ch/rss',
    'letemps': 'https://www.letemps.ch/rss',
    'nzz': 'https://www.nzz.ch/recent.rss'
}

# Ключові слова для пошуку новин про Україну
UKRAINE_KEYWORDS = [
    "Україна", "українці", "Ukraine", "Ukrainer", "Ukrainiens",
    "Kyiv", "Kiev", "Zelensky", "Zelenskyy", "Зеленський", "Status S"
]

# Prompts для GPT-4
GPT_PROMPTS = {
    'classification': """
Проаналізуй наступний текст новини та визнач, чи стосується він України або українців.
Відповідь має бути лише "Ukraine-related" або "Not related".

Текст новини:
---
{text}
---

Відповідь:""",

    'translation': """
Переклади наступний текст українською мовою, зберігаючи офіційний новинний стиль.
Уникай художнього переосмислення, дотримуйся нейтрального тону.

Текст:
---
{original_text}
---

Переклад:""",

    'summary': """
Сформулюй короткий синопсис цієї новини українською мовою, 3–5 речень. 
Включи: хто, що, де/коли, чому важливо.

Текст:
---
{translated_text}
---

Синопсис:""",

    'telegram_post': """
Створи Telegram-пост на основі наданої інформації. Використай наступний формат:

📢 *{title}*

{summary}

---
*Повний текст:*
{full_text}

[Оригінал тут]({source_url})

Заголовок: {title}
Синопсис: {summary}
Повний текст: {full_text}
Посилання: {source_url}

Telegram-пост:"""
}

# Налаштування OpenAI
OPENAI_MODEL = "gpt-4"
OPENAI_MAX_TOKENS = 2000
OPENAI_TEMPERATURE = 0.3
