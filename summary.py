"""Резюмування статей через OpenAI API"""

import openai
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class Summarizer:
    """Клас для створення синопсисів статей"""
    
    def __init__(self, api_key: str):
        """
        Ініціалізація резюматора
        
        Args:
            api_key: OpenAI API ключ
        """
        self.client = openai.OpenAI(api_key=api_key)
    
    def create_summary(self, text: str) -> Optional[str]:
        """
        Створює короткий синопсис статті українською
        
        Args:
            text: Перекладений текст статті
            
        Returns:
            Синопсис або None у разі помилки
        """
        if not text.strip():
            logger.warning("Порожній текст для резюмування")
            return None
        
        prompt = """Сформулюй розгорнутий синопсис цієї новини українською мовою (5–8 речень).

Включи обов'язково:
- Хто (головні дійові особи)
- Що (основна подія)
- Де/Коли (місце та час)
- Чому важливо (значення події)
- Контекст та наслідки

Стиль: інформативний, детальний, зрозумілий, нейтральний.

Текст новини:
---
{text}
---

Розгорнутий синопсис:""".format(text=text)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            
            if summary:
                logger.info(f"Синопсис створено ({len(summary)} символів)")
                return summary
            else:
                logger.error("GPT повернув порожній синопсис")
                return None
                
        except Exception as e:
            logger.error(f"Помилка створення синопсису: {e}")
            return None
    
    def create_summary_from_parts(self, title: str, description: str, 
                                 full_text: str = None) -> Optional[str]:
        """
        Створює синопсис з різних частин статті
        
        Args:
            title: Заголовок українською
            description: Опис українською
            full_text: Повний текст українською (опціонально)
            
        Returns:
            Синопсис або None у разі помилки
        """
        # Формуємо текст для резюмування
        text_parts = []
        
        if title:
            text_parts.append(f"Заголовок: {title}")
        
        if description:
            text_parts.append(f"Опис: {description}")
        
        if full_text:
            # Якщо повний текст довгий, беремо перші 2000 символів
            if len(full_text) > 2000:
                text_parts.append(f"Текст: {full_text[:2000]}...")
            else:
                text_parts.append(f"Текст: {full_text}")
        
        if not text_parts:
            logger.warning("Немає тексту для резюмування")
            return None
        
        combined_text = "\n\n".join(text_parts)
        return self.create_summary(combined_text)


def main():
    """Тестування резюматора"""
    import os
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Встановіть OPENAI_API_KEY для тестування")
        return
    
    summarizer = Summarizer(api_key)
    
    # Тестовий текст
    test_text = """
    Швейцарський уряд оголосив про надання додаткової гуманітарної допомоги Україні 
    в розмірі 50 мільйонів швейцарських франків. Кошти будуть спрямовані на підтримку 
    біженців та відновлення критичної інфраструктури. Рішення було прийнято на 
    засіданні Федеральної ради у Берні в середу. Це рішення є частиною більш широкої 
    програми підтримки України з боку Швейцарії, яка вже надала понад 200 мільйонів 
    франків гуманітарної допомоги з початку конфлікту.
    """
    
    summary = summarizer.create_summary(test_text.strip())
    
    print("Оригінальний текст:")
    print(test_text.strip())
    print("\nСинопсис:")
    print(summary)
    
    # Тест з частинами
    print("\n" + "="*50)
    print("Тест з частинами статті:")
    
    title = "Швейцарія надає додаткову допомогу Україні"
    description = "Федеральна рада схвалила виділення 50 млн франків"
    
    summary2 = summarizer.create_summary_from_parts(title, description, test_text.strip())
    print(f"\nСинопсис з частин: {summary2}")


if __name__ == "__main__":
    main()
