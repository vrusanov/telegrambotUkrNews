#!/usr/bin/env python3
"""Тест OpenAI API ключа"""

import os
import sys
from openai import OpenAI

def test_openai_api():
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ OPENAI_API_KEY не встановлено")
        return False
    
    print(f"🔍 Тестуємо OpenAI API...")
    print(f"API Key: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Простий тест запит
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'Hello' in Ukrainian"}
            ],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ OpenAI відповідь: {result}")
        print(f"✅ Використано токенів: {response.usage.total_tokens}")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка OpenAI API: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Тест OpenAI API")
    print("=" * 40)
    
    success = test_openai_api()
    
    if success:
        print("\n🎉 OpenAI API працює!")
        print("Перевірте логи на https://platform.openai.com/usage")
    else:
        print("\n💥 OpenAI API не працює.")
        print("Перевірте API ключ та баланс.")
    
    sys.exit(0 if success else 1)
