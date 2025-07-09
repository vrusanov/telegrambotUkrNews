# 🇨🇭🇺🇦 Swiss News Ukraine Bot

Автоматичний парсер швейцарських новин про Україну з публікацією в Telegram.

## Функції
- Щоденний парсинг RSS (7 швейцарських джерел)
- Розширена фільтрація новин про Україну та Статус S
- Переклад українською через GPT-3.5
- Розгорнуті синопсиси (5-8 речень)
- Публікація в Telegram з хештегами

## RSS Джерела

| Джерело | URL | Мова | Опис |
|---------|-----|------|------|
| SwissInfo | https://www.swissinfo.ch/eng/rss | EN | Офіційний портал Швейцарії |
| SRF News | https://www.srf.ch/news/rss | DE | Швейцарське радіо та телебачення |
| RTS Info | https://www.rts.ch/info/rss.xml | FR | Французькомовне телебачення |
| 20 Minuten | https://www.20min.ch/rss | DE | Популярна німецькомовна газета |
| Blick | https://www.blick.ch/rss.xml | DE | Швейцарська таблоїдна газета |
| NZZ | https://www.nzz.ch/recent.rss | DE | Neue Zürcher Zeitung |
| Watson | https://www.watson.ch/rss | DE | Онлайн-медіа платформа |

## Ключові слова

### Німецька (DE)
- `Ukrain(ern|er|e)` - українці, українська
- `Schutzstatus S` - статус захисту S
- `Abstimmung`, `Volksabstimmung` - голосування
- `Flüchtling(e)`, `Geflüchtete` - біженці
- `Asyl`, `humanitär`, `Integration` - притулок, гуманітарний, інтеграція

### Французька (FR)
- `Ukraini(en|enne)s?` - українці
- `statut S` - статус S
- `votation`, `référendum` - голосування
- `réfugié(e)s`, `asile` - біженці, притулок
- `humanitaire`, `intégration` - гуманітарний, інтеграція

### Англійська (EN)
- `Ukrainian(s)?` - українці
- `status S` - статус S
- `vote`, `referendum` - голосування
- `refugee(s)`, `asylum` - біженці, притулок
- `humanitarian`, `integration` - гуманітарний, інтеграція

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
