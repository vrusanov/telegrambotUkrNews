# 🇨🇭🇺🇦 Swiss News Ukraine Bot

Автоматичний парсер швейцарських новин про Україну з публікацією в Telegram.

## Функції
- Щоденний парсинг RSS (Swissinfo, Le Temps, 20min, NZZ)
- Фільтрація новин про Україну
- Переклад українською через GPT-3.5
- Публікація в Telegram

## Запуск

```bash
git clone https://github.com/vrusanov/telegrambotUkrNews.git
cd telegrambotUkrNews
pip install -r requirements.txt
cp .env.example .env
# Відредагуйте .env
python main_mvp.py
```

## GitHub Actions

1. Fork репозиторію
2. Додайте секрети в Settings → Secrets:
   - `OPENAI_API_KEY`
   - `TELEGRAM_TOKEN`
   - `TELEGRAM_CHANNEL`
3. Workflow запускається щодня о 07:00 UTC

## Файли

- `main_mvp.py` - основний скрипт
- `parser.py` - парсер RSS
- `translate.py` - переклад через OpenAI
- `summary.py` - резюмування
- `telegram_client.py` - Telegram API
