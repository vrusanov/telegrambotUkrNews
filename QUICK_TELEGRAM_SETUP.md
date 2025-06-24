# 🚨 Швидке налаштування TELEGRAM_CHANNEL

## Проблема
```
ValueError: Відсутні змінні середовища: ['telegram_channel']
```

## ⚡ Швидке рішення

### 1. Створіть Telegram канал (якщо ще немає)

**Варіант A: Публічний канал**
1. Відкрийте Telegram
2. Створіть новий канал
3. Встановіть публічне ім'я: `@your_channel_name`
4. Використовуйте `@your_channel_name` як TELEGRAM_CHANNEL

**Варіант B: Приватний канал**
1. Створіть приватний канал
2. Додайте [@userinfobot](https://t.me/userinfobot) до каналу
3. Отримайте ID каналу (формат: `-1001234567890`)
4. Видаліть @userinfobot з каналу
5. Використовуйте ID як TELEGRAM_CHANNEL

**Варіант C: Особисті повідомлення (для тестування)**
1. Напишіть [@userinfobot](https://t.me/userinfobot) особисто
2. Отримайте ваш user ID (формат: `123456789`)
3. Використовуйте ID як TELEGRAM_CHANNEL

### 2. Створіть Telegram бота

1. Напишіть [@BotFather](https://t.me/BotFather)
2. Відправте `/newbot`
3. Введіть назву: `Swiss News UA Bot`
4. Введіть username: `swiss_news_ua_bot` (має бути унікальним)
5. Отримайте токен (формат: `1234567890:ABC-DEF...`)

### 3. Додайте бота до каналу

1. Перейдіть до вашого каналу
2. Натисніть на назву каналу → Manage Channel → Administrators
3. Add Administrator → знайдіть вашого бота
4. Надайте права: ✅ Post Messages

### 4. Додайте секрети в GitHub

1. Перейдіть до https://github.com/vrusanov/telegrambotUkrNews
2. Settings → Secrets and variables → Actions
3. New repository secret

**Додайте 3 секрети:**

#### OPENAI_API_KEY
- Name: `OPENAI_API_KEY`
- Secret: `sk-...` (ваш OpenAI ключ)

#### TELEGRAM_TOKEN  
- Name: `TELEGRAM_TOKEN`
- Secret: `1234567890:ABC-DEF...` (токен бота)

#### TELEGRAM_CHANNEL
- Name: `TELEGRAM_CHANNEL`
- Secret: `@your_channel` або `-1001234567890` або `123456789`

## 🧪 Тестування

Після додавання секретів:

1. Перейдіть до Actions → "Test secrets availability"
2. Run workflow
3. Перевірте результат:

```
✅ OPENAI_API_KEY is set
✅ TELEGRAM_TOKEN is set  
✅ TELEGRAM_CHANNEL is set (value: @your_channel)
🎉 All required secrets are properly configured!
```

## 🚀 Запуск основного workflow

1. Actions → "Daily Swiss News Parser"
2. Run workflow
3. Перевірте логи - має бути:

```
🔍 Checking secrets availability...
✅ OPENAI_API_KEY is set
✅ TELEGRAM_TOKEN is set
✅ TELEGRAM_CHANNEL is set
📡 Парсинг RSS-стрічок...
📰 Знайдено X статей про Україну
📱 Публікація в Telegram...
```

## 📱 Приклади TELEGRAM_CHANNEL

| Тип | Формат | Приклад |
|-----|--------|---------|
| Публічний канал | `@channel_name` | `@swiss_news_ua` |
| Приватний канал | `-100XXXXXXXXX` | `-1001234567890` |
| Особисті повідомлення | `XXXXXXXXX` | `123456789` |
| Група | `-XXXXXXXXX` | `-987654321` |

## ⚠️ Часті помилки

### "Chat not found"
- Переконайтеся, що бот доданий до каналу як адміністратор
- Перевірте правильність ID каналу

### "Bot was blocked by the user"  
- Якщо використовуєте особисті повідомлення, напишіть боту `/start`

### "Not enough rights to send text messages"
- Надайте боту права "Post Messages" в каналі

## 🎯 Швидкий тест

Для швидкого тестування використовуйте особисті повідомлення:

1. Напишіть [@userinfobot](https://t.me/userinfobot) → отримайте ваш ID
2. Створіть бота через [@BotFather](https://t.me/BotFather)
3. Напишіть вашому боту `/start`
4. Використовуйте ваш ID як TELEGRAM_CHANNEL
5. Запустіть workflow

**Після налаштування секретів workflow буде працювати! 🎉**
