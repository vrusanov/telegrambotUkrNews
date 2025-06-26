"""OpenAI API для перекладу та класифікації"""

import openai
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class Translator:
    """Клас для перекладу текстів через OpenAI API"""
    
    def __init__(self, api_key: str):
        """
        Ініціалізація перекладача
        
        Args:
            api_key: OpenAI API ключ
        """
        self.client = openai.OpenAI(api_key=api_key)
    
    def classify_ukraine_related(self, text: str) -> str:
        """
        GPT-класифікатор для визначення релевантності до України
        
        Args:
            text: Текст для класифікації
            
        Returns:
            "Ukraine-related" або "Other"
        """
        prompt = """Classify the text as "Ukraine-related" or "Other".

Text is "Ukraine-related" if it mentions:
- Ukraine, Ukrainian people, Ukrainian cities
- Ukrainian government officials (Zelensky, etc.)
- Military actions in Ukraine
- Humanitarian aid to Ukraine
- Ukrainian refugees in Switzerland
- Status S (Schutzstatus S, statut S) for Ukrainians
- Voting/referendum about Ukrainian refugees
- Economic sanctions related to Ukraine war
- Swiss-Ukrainian relations

Respond with only "Ukraine-related" or "Other".

Text:
---
{text}
---

Classification:""".format(text=text)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            logger.info(f"GPT класифікація: {result}")
            
            return "Ukraine-related" if "Ukraine-related" in result else "Other"
            
        except Exception as e:
            logger.error(f"Помилка GPT класифікації: {e}")
            return "Other"
    
    def translate_to_ukrainian(self, text: str, source_language: str = "auto") -> Optional[str]:
        """
        Перекладає текст українською мовою
        
        Args:
            text: Текст для перекладу
            source_language: Мова оригіналу (auto для автовизначення)
            
        Returns:
            Перекладений текст або None у разі помилки
        """
        if not text.strip():
            return None
        
        # Формуємо промпт залежно від мови
        if source_language == "de":
            lang_instruction = "з німецької на українську"
        elif source_language == "fr":
            lang_instruction = "з французької на українську"
        elif source_language == "it":
            lang_instruction = "з італійської на українську"
        elif source_language == "en":
            lang_instruction = "з англійської на українську"
        else:
            lang_instruction = "українською мовою"
        
        prompt = f"""Переклади текст {lang_instruction}, зберігаючи офіційний новинний стиль.

Вимоги:
- Дотримуйся точності фактів
- Використовуй нейтральний тон
- Зберігай структуру тексту
- Уникай художніх інтерпретацій

Текст для перекладу:
---
{text}
---

Переклад українською:"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            translation = response.choices[0].message.content.strip()
            
            if translation:
                logger.info(f"Переклад виконано ({len(translation)} символів)")
                return translation
            else:
                logger.error("GPT повернув порожній переклад")
                return None
                
        except Exception as e:
            logger.error(f"Помилка перекладу: {e}")
            return None


def main():
    """Тестування перекладача"""
    import os
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Встановіть OPENAI_API_KEY для тестування")
        return
    
    translator = Translator(api_key)
    
    # Тест класифікації
    test_text = "Switzerland provides humanitarian aid to Ukraine worth 50 million francs"
    classification = translator.classify_ukraine_related(test_text)
    print(f"Класифікація: {classification}")
    
    # Тест перекладу
    test_texts = {
        'de': "Die Schweiz unterstützt die Ukraine mit humanitärer Hilfe.",
        'fr': "La Suisse soutient l'Ukraine avec une aide humanitaire.",
        'en': "Switzerland supports Ukraine with humanitarian aid."
    }
    
    for lang, text in test_texts.items():
        translation = translator.translate_to_ukrainian(text, lang)
        print(f"\n{lang}: {text}")
        print(f"UA: {translation}")


if __name__ == "__main__":
    main()
