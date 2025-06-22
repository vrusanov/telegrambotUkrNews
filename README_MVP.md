# telegram-news-ua-ch

Автоматичний парсер швейцарських новин про Україну з публікацією в Telegram.

## Опис

Цей MVP автоматично:
1. **Щодня о 07:00 UTC** парсить RSS-стрічки швейцарських новинних сайтів
2. Визначає мову статті та фільтрує новини про Україну
3. Завантажує повний текст, перекладає українською та створює синопсис
4. Публікує у Telegram-каналі з Markdown форматуванням
5. Логує ID опублікованих постів для уникнення дублювання
6. Працює автономно на GitHub Actions (безкоштовно)

## Джерела новин

- **SwissInfo.ch** - офіційний новинний портал Швейцарії
- **Le Temps** - провідна французькомовна газета
- **20 Minuten** - популярне німецькомовне видання
- **NZZ** - Neue Zürcher Zeitung

## Структура проекту

```
telegram-news-ua-ch/
├── main_mvp.py              # Точка входу з усім пайплайном
├── parser.py                # RSS/HTML парсер (feedparser + BeautifulSoup)
├── translate.py             # Обгортка OpenAI API для перекладу
├── summary.py               # Резюмування статті
├── telegram_client.py       # Надсилання повідомлень через Bot API
├── .github/workflows/daily-news-parser.yml  # GitHub Actions workflow
├── requirements_mvp.txt     # Залежності
├── .env_mvp.example         # Приклад змінних середовища
├── data/seen.json           # Опрацьовані URL (створюється автоматично)
├── logs/app.log             # Логи (створюється автоматично)
└── README_MVP.md            # Ця документація
```

## Швидкий старт

### 1. Клонування репозиторію
```bash
git clone https://github.com/your-username/telegram-news-ua-ch.git
cd telegram-news-ua-ch
```

### 2. Встановлення залежностей
```bash
pip install -r requirements_mvp.txt
```

### 3. Налаштування змінних середовища
```bash
cp .env_mvp.example .env
```

Відредагуйте `.env` файл:
```bash
OPENAI_API_KEY=your-openai-api-key-here
TELEGRAM_TOKEN=your-telegram-bot-token-here
TELEGRAM_CHANNEL=your-telegram-channel-id-here
```

### 4. Локальний запуск
```bash
python main_mvp.py
```

## Налаштування Telegram

### 1. Створення бота
1. Напишіть [@BotFather](https://t.me/BotFather) в Telegram
2. Виконайте команду `/newbot`
3. Дайте назву та username боту
4. Отримайте токен бота

### 2. Налаштування каналу
1. Створіть Telegram канал
2. Додайте бота як адміністратора з правами публікації
3. Отримайте ID каналу:
   - Для публічних каналів: `@channel_username`
   - Для приватних: `-1001234567890` (отримайте через [@userinfobot](https://t.me/userinfobot))

## Розгортання на GitHub Actions

### 1. Fork репозиторію
Створіть fork цього репозиторію у своєму GitHub акаунті.

### 2. Налаштування секретів
Перейдіть до Settings → Secrets and variables → Actions та додайте:

- `OPENAI_API_KEY` - ваш OpenAI API ключ
- `TELEGRAM_TOKEN` - токен Telegram бота
- `TELEGRAM_CHANNEL` - ID Telegram каналу

### 3. Активація workflow
GitHub Actions автоматично запуститься щодня о 07:00 UTC.

Для ручного запуску:
1. Перейдіть до вкладки Actions
2. Виберіть "Daily Swiss News Parser"
3. Натисніть "Run workflow"

## Технічні деталі

### GPT Промпти

**1. Класифікатор:**
```
Classify the text as "Ukraine-related" or "Other".

Text is "Ukraine-related" if it mentions:
- Ukraine, Ukrainian people, Ukrainian cities
- Ukrainian government officials (Zelensky, etc.)
- Military actions in Ukraine
- Humanitarian aid to Ukraine
- Ukrainian refugees
- Economic sanctions related to Ukraine war

Respond with only "Ukraine-related" or "Other".
```

**2. Переклад:**
```
Переклади текст [з мови] на українську, зберігаючи офіційний новинний стиль.

Вимоги:
- Дотримуйся точності фактів
- Використовуй нейтральний тон
- Зберігай структуру тексту
- Уникай художніх інтерпретацій
```

**3. Синопсис:**
```
Сформулюй короткий синопсис цієї новини українською мовою (3–5 речень).

Включи обов'язково:
- Хто (головні дійові особи)
- Що (основна подія)
- Де/Коли (місце та час)
- Чому важливо (значення події)
```

### Формат Telegram повідомлення

```markdown
📢 *Заголовок українською*

Синопсис новини (3-5 речень з ключовими фактами)

---
*Повний текст:*
Перекладений повний текст статті...

[Читати оригінал](посилання)

Джерело: swissinfo
```

### Логування

Система логує всі дії у:
- **Консоль** - для моніторингу в реальному часі
- **logs/app.log** - для збереження історії
- **data/seen.json** - для відстеження опублікованих URL

### Уникнення дублювання

Система зберігає URL опублікованих статей у `data/seen.json` та перевіряє їх перед публікацією.

## Моніторинг

### Перевірка логів
```bash
# Останні логи
tail -f logs/app.log

# Опубліковані URL
cat data/seen.json
```

### GitHub Actions
Перевіряйте статус виконання у вкладці Actions вашого репозиторію.

## Troubleshooting

### Помилки OpenAI API
- Перевірте правильність API ключа
- Перевірте баланс на OpenAI акаунті
- Перевірте ліміти запитів

### Помилки Telegram
- Перевірте правильність токена бота
- Переконайтеся, що бот доданий до каналу як адміністратор
- Перевірте правильність ID каналу

### Помилки парсингу
- Деякі сайти можуть тимчасово блокувати автоматичні запити
- RSS-стрічки можуть змінювати формат

## Ліцензія

MIT License

## Підтримка

Для питань та проблем створюйте Issues у GitHub репозиторії.
