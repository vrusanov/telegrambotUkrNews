# Налаштування Google Sheets інтеграції

## Крок 1: Створення Google Cloud проекту

1. Перейдіть на [Google Cloud Console](https://console.cloud.google.com/)
2. Створіть новий проект або виберіть існуючий
3. Запишіть ID проекту

## Крок 2: Увімкнення Google Sheets API

1. В Google Cloud Console перейдіть до "APIs & Services" > "Library"
2. Знайдіть "Google Sheets API"
3. Натисніть "Enable"
4. Також увімкніть "Google Drive API"

## Крок 3: Створення Service Account

1. Перейдіть до "APIs & Services" > "Credentials"
2. Натисніть "Create Credentials" > "Service Account"
3. Заповніть форму:
   - **Service account name**: `swiss-news-parser`
   - **Service account ID**: `swiss-news-parser`
   - **Description**: `Service account for Swiss news parser`
4. Натисніть "Create and Continue"
5. Пропустіть налаштування ролей (натисніть "Continue")
6. Натисніть "Done"

## Крок 4: Створення ключа для Service Account

1. В списку Service Accounts знайдіть щойно створений
2. Натисніть на email Service Account
3. Перейдіть на вкладку "Keys"
4. Натисніть "Add Key" > "Create new key"
5. Виберіть формат "JSON"
6. Натисніть "Create"
7. Файл `credentials.json` буде завантажено на ваш комп'ютер

## Крок 5: Налаштування файлу credentials

1. Перемістіть завантажений файл в директорію проекту
2. Перейменуйте його на `credentials.json`
3. Переконайтеся, що файл має правильну структуру:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "swiss-news-parser@your-project-id.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

## Крок 6: Створення Google таблиці

1. Перейдіть на [Google Sheets](https://sheets.google.com/)
2. Створіть нову таблицю
3. Дайте їй назву, наприклад "Swiss News Moderation"
4. Скопіюйте ID таблиці з URL:
   ```
   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
   ```

## Крок 7: Надання доступу Service Account

1. В Google таблиці натисніть "Share" (Поділитися)
2. В поле email введіть email вашого Service Account:
   ```
   swiss-news-parser@your-project-id.iam.gserviceaccount.com
   ```
3. Виберіть роль "Editor" (Редактор)
4. Зніміть галочку "Notify people" (не надсилати сповіщення)
5. Натисніть "Share"

## Крок 8: Налаштування змінних середовища

Додайте в файл `.env`:

```bash
GOOGLE_CREDENTIALS_PATH=credentials.json
GOOGLE_SPREADSHEET_ID=your-spreadsheet-id-here
```

## Крок 9: Тестування підключення

Запустіть тестовий скрипт:

```bash
python -c "
from google_sheets_integration import GoogleSheetsManager
import os

credentials_path = 'credentials.json'
spreadsheet_id = os.getenv('GOOGLE_SPREADSHEET_ID')

if os.path.exists(credentials_path) and spreadsheet_id:
    try:
        manager = GoogleSheetsManager(credentials_path, spreadsheet_id)
        print('✅ Google Sheets підключено успішно!')
    except Exception as e:
        print(f'❌ Помилка: {e}')
else:
    print('⚠️ Перевірте credentials.json та GOOGLE_SPREADSHEET_ID')
"
```

## Структура таблиці

Після першого запуску в таблиці автоматично створяться колонки:

| A | B | C | D | E | F | G | H | I | J |
|---|---|---|---|---|---|---|---|---|---|
| Timestamp | Source | Title | Summary | FullText | Link | Approved | Published | Notes | Image_Generated |

### Опис колонок:

- **Timestamp**: Дата та час додавання
- **Source**: Джерело новини (swissinfo, 20min, letemps)
- **Title**: Заголовок українською
- **Summary**: Короткий синопсис
- **FullText**: Повний текст українською
- **Link**: Посилання на оригінал
- **Approved**: Схвалено (Yes/No) - **редагуйте цю колонку для модерації**
- **Published**: Опубліковано (Yes/No) - автоматично
- **Notes**: Примітки модератора
- **Image_Generated**: Чи згенеровано зображення (Yes/No)

## Workflow модерації

1. **Автоматичне додавання**: Скрипт додає нові статті з `Approved = No`
2. **Модерація**: Редактор змінює `Approved` на `Yes` для схвалених статей
3. **Публікація**: Скрипт `publish_approved_news.py` публікує схвалені статті
4. **Позначення**: Після публікації `Published` змінюється на `Yes`

## Команди для роботи

```bash
# Парсинг та збереження в Google Sheets
python news_workflow_manager.py

# Публікація схвалених статей
python publish_approved_news.py

# Тестування Google Sheets
python google_sheets_integration.py
```

## Troubleshooting

### Помилка аутентифікації
```
google.auth.exceptions.DefaultCredentialsError
```
**Рішення**: Перевірте шлях до `credentials.json` та права доступу

### Помилка доступу до таблиці
```
gspread.exceptions.SpreadsheetNotFound
```
**Рішення**: 
1. Перевірте правильність SPREADSHEET_ID
2. Переконайтеся, що Service Account має доступ до таблиці

### Помилка API
```
gspread.exceptions.APIError: [403]
```
**Рішення**: 
1. Увімкніть Google Sheets API та Google Drive API
2. Перевірте квоти API в Google Cloud Console

### Помилка прав доступу
```
gspread.exceptions.APIError: [400] Unable to parse range
```
**Рішення**: Переконайтеся, що таблиця існує та має правильну структуру

## Безпека

1. **Не додавайте `credentials.json` в git**:
   ```bash
   echo "credentials.json" >> .gitignore
   ```

2. **Обмежте права Service Account**:
   - Надавайте доступ тільки до потрібних таблиць
   - Використовуйте роль "Editor", а не "Owner"

3. **Регулярно оновлюйте ключі**:
   - Створюйте нові ключі кожні 90 днів
   - Видаляйте старі ключі

## Моніторинг

Перевіряйте логи для відстеження роботи:

```bash
# Логи збереження в Google Sheets
tail -f swiss_news.log | grep "Google Sheets"

# Логи публікації
tail -f publish_approved.log
```
