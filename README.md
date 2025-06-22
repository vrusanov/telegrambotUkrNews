# 🇨🇭🇺🇦 Telegram Bot для швейцарських новин про Україну

Автоматичний парсер RSS-стрічок швейцарських новинних сайтів з фільтрацією новин про Україну, перекладом українською мовою та публікацією в Telegram.

## 🎯 MVP готовий до використання!

**Повний функціонал реалізовано згідно з технічними вимогами:**
- ✅ Щоденний парсинг о 07:00 UTC (GitHub Actions)
- ✅ 4 швейцарські джерела: Swissinfo, Le Temps, 20min, NZZ
- ✅ Визначення мови + фільтрація про Україну
- ✅ Переклад українською через GPT-3.5
- ✅ Публікація в Telegram з Markdown форматуванням
- ✅ Уникнення дублювання

## 🚀 Швидкий старт

### 1. Клонування
```bash
git clone https://github.com/vrusanov/telegrambotUkrNews.git
cd telegrambotUkrNews
```

### 2. Встановлення залежностей
```bash
pip install -r requirements_mvp.txt
```

### 3. Налаштування
```bash
cp .env_mvp.example .env
# Відредагуйте .env з вашими API ключами
```

### 4. Запуск
```bash
python main_mvp.py
```

## 📋 Налаштування GitHub Actions

1. **Fork цього репозиторію**
2. **Додайте секрети** в Settings → Secrets and variables → Actions:
   - `OPENAI_API_KEY` - ваш OpenAI API ключ
   - `TELEGRAM_TOKEN` - токен Telegram бота
   - `TELEGRAM_CHANNEL` - ID Telegram каналу
3. **Активуйте workflow** - він запуститься автоматично щодня о 07:00 UTC

Детальні інструкції: [GITHUB_SECRETS_SETUP.md](GITHUB_SECRETS_SETUP.md)

## 🔧 Структура проекту

### MVP файли (згідно з технічними вимогами):
- `main_mvp.py` - точка входу з усім пайплайном
- `parser.py` - RSS/HTML парсер (feedparser + BeautifulSoup)
- `translate.py` - обгортка OpenAI API
- `summary.py` - резюмування статті
- `telegram_client.py` - надсилання повідомлень
- `.github/workflows/daily-news-parser.yml` - workflow із cron
- `requirements_mvp.txt` - залежності
- `.env_mvp.example` - змінні середовища

### Розширені функції:
- `main.py` - розширений workflow з Google Sheets та DALL-E
- `google_sheets_integration.py` - модерація через Google Sheets
- `dalle_image_generator.py` - генерація зображень
- `telegram_bot_advanced.py` - розширений Telegram бот

## 📱 Налаштування Telegram

### Створення бота:
1. Напишіть [@BotFather](https://t.me/BotFather)
2. Виконайте `/newbot`
3. Отримайте токен бота

### Налаштування каналу:
1. Створіть канал
2. Додайте бота як адміністратора
3. Отримайте ID каналу

Детальні інструкції: [GITHUB_SECRETS_SETUP.md](GITHUB_SECRETS_SETUP.md)

## 🌐 Джерела новин

- **SwissInfo.ch** - офіційний портал Швейцарії
- **Le Temps** - провідна французькомовна газета
- **20 Minuten** - популярне німецькомовне видання
- **NZZ** - Neue Zürcher Zeitung

## 🧪 Тестування

Перевірте налаштування секретів:
1. Перейдіть до Actions → "Test secrets availability"
2. Натисніть "Run workflow"
3. Перевірте результати

## 📊 Формат Telegram повідомлення

```markdown
📢 *Заголовок українською*

Синопсис новини (3-5 речень)

---
*Повний текст:*
Перекладений текст...

[Читати оригінал](посилання)
Джерело: swissinfo
```

## 🔄 Workflow

1. **Парсинг RSS** - щодня о 07:00 UTC
2. **Визначення мови** - langdetect
3. **Фільтрація** - ключові слова + GPT
4. **Завантаження тексту** - BeautifulSoup
5. **Переклад** - OpenAI GPT-3.5
6. **Синопсис** - 3-5 речень
7. **Публікація** - Telegram з Markdown V2
8. **Логування** - уникнення дублювання

## 📁 Документація

- [README_MVP.md](README_MVP.md) - детальна інструкція MVP
- [GITHUB_SECRETS_SETUP.md](GITHUB_SECRETS_SETUP.md) - налаштування секретів
- [GITHUB_PUSH_INSTRUCTIONS.md](GITHUB_PUSH_INSTRUCTIONS.md) - інструкція для пушу
- [MVP_COMPLETION_REPORT.md](MVP_COMPLETION_REPORT.md) - звіт про виконання
- [TECHNICAL_STEPS_IMPLEMENTATION.md](TECHNICAL_STEPS_IMPLEMENTATION.md) - технічні деталі
- [ADVANCED_FEATURES.md](ADVANCED_FEATURES.md) - розширені функції

## 🎯 Статус виконання

**✅ ВСЕ ВИКОНАНО ПОВНІСТЮ!**

Всі вимоги технічного завдання реалізовано:
- ✅ Структура файлів згідно з вимогами
- ✅ Використання правильних технологій
- ✅ GitHub Actions з cron `0 7 * * *`
- ✅ Повна документація та інструкції
- ✅ Тестування та готовність до продакшену

## 📞 Підтримка

Для питань створюйте Issues в цьому репозиторії.

---

**Проект готовий до використання! 🎉**
