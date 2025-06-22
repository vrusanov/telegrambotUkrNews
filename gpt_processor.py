"""
Модуль для роботи з OpenAI GPT-4
"""

import openai
from typing import Dict, Optional
import logging
from config import GPT_PROMPTS, OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE

logger = logging.getLogger(__name__)


class GPTProcessor:
    """Клас для обробки новин за допомогою GPT-4"""
    
    def __init__(self, api_key: str):
        """
        Ініціалізація GPT процесора
        
        Args:
            api_key: OpenAI API ключ
        """
        openai.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
    
    def _make_gpt_request(self, prompt: str) -> Optional[str]:
        """
        Виконує запит до GPT-4
        
        Args:
            prompt: Текст промпту
            
        Returns:
            Відповідь від GPT або None у разі помилки
        """
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=OPENAI_MAX_TOKENS,
                temperature=OPENAI_TEMPERATURE
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Помилка при запиті до GPT: {e}")
            return None
    
    def classify_news(self, text: str) -> str:
        """
        Класифікує новину як пов'язану з Україною або ні
        
        Args:
            text: Текст новини
            
        Returns:
            "Ukraine-related" або "Not related"
        """
        prompt = GPT_PROMPTS['classification'].format(text=text)
        result = self._make_gpt_request(prompt)
        
        if result and "Ukraine-related" in result:
            return "Ukraine-related"
        return "Not related"
    
    def translate_to_ukrainian(self, text: str) -> Optional[str]:
        """
        Перекладає текст українською мовою
        
        Args:
            text: Оригінальний текст
            
        Returns:
            Перекладений текст або None у разі помилки
        """
        prompt = GPT_PROMPTS['translation'].format(original_text=text)
        return self._make_gpt_request(prompt)
    
    def create_summary(self, translated_text: str) -> Optional[str]:
        """
        Створює короткий синопсис новини
        
        Args:
            translated_text: Перекладений текст новини
            
        Returns:
            Синопсис або None у разі помилки
        """
        prompt = GPT_PROMPTS['summary'].format(translated_text=translated_text)
        return self._make_gpt_request(prompt)
    
    def generate_telegram_post(self, title: str, summary: str, 
                             full_text: str, source_url: str) -> Optional[str]:
        """
        Генерує Telegram-пост
        
        Args:
            title: Заголовок українською
            summary: Синопсис
            full_text: Повний перекладений текст
            source_url: Посилання на оригінал
            
        Returns:
            Готовий Telegram-пост або None у разі помилки
        """
        # Створюємо пост безпосередньо за шаблоном
        telegram_post = f"""📢 *{title}*

{summary}

---
*Повний текст:*
{full_text}

[Оригінал тут]({source_url})"""
        
        return telegram_post
