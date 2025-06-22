# Налаштування GitHub Secrets

## 🔐 Необхідні секрети для роботи бота

Для автоматичної роботи GitHub Actions потрібно налаштувати 3 секрети:

### 1. `OPENAI_API_KEY`
- **Що це**: API ключ для OpenAI GPT-3.5-turbo
- **Де отримати**: https://platform.openai.com/api-keys
- **Формат**: `sk-...` (починається з sk-)
- **Призначення**: Переклад та резюмування новин

### 2. `TELEGRAM_TOKEN`
- **Що це**: Токен Telegram бота
- **Де отримати**: [@BotFather](https://t.me/BotFather) → `/newbot`
- **Формат**: `1234567890:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`
- **Призначення**: Публікація повідомлень в Telegram

### 3. `TELEGRAM_CHANNEL`
- **Що це**: ID каналу для публікації
- **Формати**: 
  - Публічний канал: `@channel_name`
  - Приватний канал: `-1001234567890`
- **Де отримати**: [@userinfobot](https://t.me/userinfobot) для приватних каналів
- **Призначення**: Визначення куди публікувати новини

## 📋 Покрокова інструкція

### Крок 1: Отримання OpenAI API ключа

1. Перейдіть на https://platform.openai.com/
2. Увійдіть в акаунт або зареєструйтеся
3. Перейдіть до API Keys: https://platform.openai.com/api-keys
4. Натисніть "Create new secret key"
5. Дайте назву ключу: `telegrambotUkrNews`
6. Скопіюйте ключ (починається з `sk-`)
7. **ВАЖЛИВО**: Переконайтеся, що у вас є кредити на балансі

### Крок 2: Створення Telegram бота

1. Напишіть [@BotFather](https://t.me/BotFather) в Telegram
2. Відправте команду `/newbot`
3. Введіть назву бота: `Swiss News UA Bot`
4. Введіть username бота: `swiss_news_ua_bot` (має бути унікальним)
5. Отримайте токен бота (формат: `1234567890:ABC-DEF...`)
6. Збережіть токен в безпечному місці

### Крок 3: Налаштування Telegram каналу

#### Варіант A: Публічний канал
1. Створіть публічний канал в Telegram
2. Встановіть username каналу: `@your_channel_name`
3. Додайте бота як адміністратора з правами публікації
4. Використовуйте `@your_channel_name` як TELEGRAM_CHANNEL

#### Варіант B: Приватний канал
1. Створіть приватний канал в Telegram
2. Додайте бота як адміністратора
3. Додайте [@userinfobot](https://t.me/userinfobot) до каналу
4. Отримайте ID каналу (формат: `-1001234567890`)
5. Видаліть @userinfobot з каналу
6. Використовуйте ID як TELEGRAM_CHANNEL

### Крок 4: Додавання секретів в GitHub

1. Перейдіть до вашого репозиторію на GitHub
2. Натисніть **Settings** (вкладка в репозиторії)
3. В лівому меню виберіть **Secrets and variables** → **Actions**
4. Натисніть **New repository secret**
5. Додайте кожен секрет:

#### OPENAI_API_KEY
- **Name**: `OPENAI_API_KEY`
- **Secret**: ваш OpenAI ключ (sk-...)

#### TELEGRAM_TOKEN
- **Name**: `TELEGRAM_TOKEN`
- **Secret**: ваш Telegram bot token

#### TELEGRAM_CHANNEL
- **Name**: `TELEGRAM_CHANNEL`
- **Secret**: ID або username каналу

## 🧪 Тестування секретів

Після додавання всіх секретів:

1. Перейдіть до вкладки **Actions** в репозиторії
2. Виберіть workflow **"Test secrets availability"**
3. Натисніть **"Run workflow"** → **"Run workflow"**
4. Дочекайтеся завершення (зелена галочка)
5. Перевірте логи - мають бути ✅ для всіх секретів

### Очікуваний результат:
```
✅ OPENAI_API_KEY detected (length=51)
✅ TELEGRAM_TOKEN detected (length=46)
✅ TELEGRAM_CHANNEL detected (value=@your_channel)
🎉 All required secrets are properly configured!
```

## ⚠️ Безпека

### Що НІКОЛИ не робити:
- ❌ Не додавайте секрети в код
- ❌ Не коммітьте .env файли з реальними ключами
- ❌ Не діліться секретами в Issues або Pull Requests
- ❌ Не логуйте повні значення секретів

### Що робити:
- ✅ Використовуйте тільки GitHub Secrets
- ✅ Регулярно оновлюйте API ключі
- ✅ Видаляйте невикористовувані секрети
- ✅ Обмежуйте права Telegram бота

## 🔄 Після налаштування

1. **Запустіть тест секретів** (workflow "Test secrets availability")
2. **Запустіть основний workflow** (workflow "Daily Swiss News Parser")
3. **Перевірте канал** - мають з'явитися новини
4. **Налаштуйте розклад** - workflow запускається щодня о 07:00 UTC

## 🆘 Troubleshooting

### Помилка: "OPENAI_API_KEY is NOT set"
- Перевірте правильність назви секрету
- Переконайтеся, що ключ починається з `sk-`
- Перевірте баланс на OpenAI акаунті

### Помилка: "TELEGRAM_TOKEN is NOT set"
- Перевірте формат токену (має містити `:`)
- Переконайтеся, що бот створений через @BotFather

### Помилка: "TELEGRAM_CHANNEL is NOT set"
- Для публічних каналів: `@channel_name`
- Для приватних каналів: `-1001234567890`
- Переконайтеся, що бот доданий як адміністратор

### Бот не публікує повідомлення
- Перевірте права бота в каналі
- Переконайтеся, що канал існує
- Перевірте логи GitHub Actions

## 📞 Підтримка

Якщо виникають проблеми:
1. Запустіть workflow "Test secrets availability"
2. Перевірте логи в Actions
3. Створіть Issue з описом проблеми та скріншотами логів

---

**Після налаштування всіх секретів бот буде працювати автоматично! 🤖**
