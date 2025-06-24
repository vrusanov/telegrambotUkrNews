#!/usr/bin/env python3
"""Тест Telegram бота"""

import os
import sys
from telegram_client import TelegramClient

def test_telegram():
    token = os.getenv('TELEGRAM_TOKEN')
    channel = os.getenv('TELEGRAM_CHANNEL')
    
    if not token:
        print("❌ TELEGRAM_TOKEN не встановлено")
        return False
    
    if not channel:
        print("❌ TELEGRAM_CHANNEL не встановлено") 
        return False
    
    print(f"🔍 Тестуємо Telegram бота...")
    print(f"Token: {token[:10]}...")
    print(f"Channel: {channel}")
    
    client = TelegramClient(token, channel)
    
    print("\n1. Тестуємо з'єднання...")
    if client.test_connection():
        print("✅ З'єднання успішне")
    else:
        print("❌ Помилка з'єднання")
        return False
    
    print("\n2. Надсилаємо тестове повідомлення...")
    message_id = client.send_message(
        title="🧪 Тестове повідомлення",
        summary="Це тест роботи Telegram бота для швейцарських новин про Україну.",
        full_text="Якщо ви бачите це повідомлення, то бот працює правильно!",
        url="https://github.com/vrusanov/telegrambotUkrNews",
        source="test"
    )
    
    if message_id:
        print(f"✅ Повідомлення надіслано! ID: {message_id}")
        print(f"Перевірте ваш канал: {channel}")
        return True
    else:
        print("❌ Не вдалося надіслати повідомлення")
        return False

if __name__ == "__main__":
    print("🤖 Тест Telegram бота")
    print("=" * 40)
    
    success = test_telegram()
    
    if success:
        print("\n🎉 Тест пройшов успішно!")
    else:
        print("\n💥 Тест не пройшов.")
    
    sys.exit(0 if success else 1)
