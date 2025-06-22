"""
Сервіс перекладу з урахуванням мови оригіналу
Реалізує крок 6 з технічного завдання
"""

import openai
import logging
from typing import Optional, Dict
from parse_news import NewsArticleWithLang

logger = logging.getLogger(__name__)


class TranslationService:
    """Сервіс для перекладу новин українською з урахуванням мови оригіналу"""
    
    def __init__(self, api_key: str):
        """
        Ініціалізація сервісу перекладу
        
        Args:
            api_key: OpenAI API ключ
        """
        self.client = openai.OpenAI(api_key=api_key)
        
        # Промпти для різних мов
        self.translation_prompts = {
            'de': """Переклади наступний текст з німецької на українську мову, зберігаючи офіційний новинний стиль.
Дотримуйся точності фактів та нейтрального тону.

Німецький текст:
---
{text}
---

Переклад українською:""",

            'fr': """Переклади наступний текст з французької на українську мову, зберігаючи офіційний новинний стиль.
Дотримуйся точності фактів та нейтрального тону.

Французький текст:
---
{text}
---

Переклад українською:""",

            'it': """Переклади наступний текст з італійської на українську мову, зберігаючи офіційний новинний стиль.
Дотримуйся точності фактів та нейтрального тону.

Італійський текст:
---
{text}
---

Переклад українською:""",

            'en': """Переклади наступний текст з англійської на українську мову, зберігаючи офіційний новинний стиль.
Дотримуйся точності фактів та нейтрального тону.

Англійський текст:
---
{text}
---

Переклад українською:""",

            'default': """Переклади наступний текст українською мовою, зберігаючи офіційний новинний стиль.
Автоматично визнач мову оригіналу та переклади точно й нейтрально.

Текст:
---
{text}
---

Переклад українською:"""
        }
    
    def _get_language_name(self, lang_code: str) -> str:
        """Повертає назву мови українською"""
        language_names = {
            'de': 'німецька',
            'fr': 'французька', 
            'it': 'італійська',
            'en': 'англійська',
            'es': 'іспанська',
            'pt': 'португальська',
            'nl': 'нідерландська',
            'sv': 'шведська',
            'no': 'норвезька',
            'da': 'данська'
        }
        return language_names.get(lang_code, f'мова ({lang_code})')
    
    def translate_to_ukrainian(self, text: str, source_lang: Optional[str] = None) -> Optional[str]:
        """
        Перекладає текст українською з урахуванням мови оригіналу
        
        Args:
            text: Текст для перекладу
            source_lang: Код мови оригіналу (de, fr, en, тощо)
            
        Returns:
            Перекладений текст або None у разі помилки
        """
        if not text.strip():
            logger.warning("Порожній текст для перекладу")
            return None
        
        try:
            # Вибираємо промпт залежно від мови
            if source_lang and source_lang in self.translation_prompts:
                prompt = self.translation_prompts[source_lang].format(text=text)
                lang_name = self._get_language_name(source_lang)
                logger.info(f"Перекладаємо з {lang_name} ({source_lang})")
            else:
                prompt = self.translation_prompts['default'].format(text=text)
                logger.info(f"Перекладаємо з автовизначенням мови (визначено: {source_lang})")
            
            # Виконуємо переклад
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            translation = response.choices[0].message.content.strip()
            
            if translation:
                logger.info(f"Переклад виконано успішно (довжина: {len(translation)} символів)")
                return translation
            else:
                logger.error("GPT повернув порожній переклад")
                return None
                
        except Exception as e:
            logger.error(f"Помилка перекладу: {e}")
            return None
    
    def translate_article(self, article: NewsArticleWithLang) -> NewsArticleWithLang:
        """
        Перекладає всі частини статті українською
        
        Args:
            article: Стаття для перекладу
            
        Returns:
            Стаття з перекладеними полями
        """
        logger.info(f"Перекладаємо статтю: {article.title}")
        
        # Перекладаємо заголовок
        if article.title:
            translated_title = self.translate_to_ukrainian(
                article.title, 
                article.detected_language
            )
            if translated_title:
                article.translated_title = translated_title
        
        # Перекладаємо опис
        if article.description:
            translated_description = self.translate_to_ukrainian(
                article.description,
                article.detected_language
            )
            if translated_description:
                article.translated_description = translated_description
        
        # Перекладаємо повний текст (якщо є)
        if article.full_text:
            # Для довгих текстів розбиваємо на частини
            if len(article.full_text) > 3000:
                logger.info("Довгий текст, перекладаємо частинами")
                translated_parts = []
                
                # Розбиваємо текст на абзаци
                paragraphs = article.full_text.split('\n\n')
                current_chunk = ""
                
                for paragraph in paragraphs:
                    if len(current_chunk + paragraph) < 3000:
                        current_chunk += paragraph + "\n\n"
                    else:
                        if current_chunk:
                            translated_part = self.translate_to_ukrainian(
                                current_chunk.strip(),
                                article.detected_language
                            )
                            if translated_part:
                                translated_parts.append(translated_part)
                        current_chunk = paragraph + "\n\n"
                
                # Перекладаємо останню частину
                if current_chunk:
                    translated_part = self.translate_to_ukrainian(
                        current_chunk.strip(),
                        article.detected_language
                    )
                    if translated_part:
                        translated_parts.append(translated_part)
                
                if translated_parts:
                    article.translated_text = "\n\n".join(translated_parts)
            else:
                translated_text = self.translate_to_ukrainian(
                    article.full_text,
                    article.detected_language
                )
                if translated_text:
                    article.translated_text = translated_text
        
        return article
    
    def summarize_article(self, text: str) -> Optional[str]:
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
        
        try:
            prompt = """Сформулюй короткий синопсис цієї новини українською мовою, 3–5 речень. 
Включи: хто, що, де/коли, чому важливо.

Текст новини:
---
{text}
---

Синопсис:""".format(text=text)
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            
            if summary:
                logger.info("Синопсис створено успішно")
                return summary
            else:
                logger.error("GPT повернув порожній синопсис")
                return None
                
        except Exception as e:
            logger.error(f"Помилка створення синопсису: {e}")
            return None
    
    def process_article_full(self, article: NewsArticleWithLang) -> NewsArticleWithLang:
        """
        Повна обробка статті: переклад + синопсис
        
        Args:
            article: Стаття для обробки
            
        Returns:
            Повністю оброблена стаття
        """
        logger.info(f"Повна обробка статті: {article.title}")
        
        # Перекладаємо статтю
        article = self.translate_article(article)
        
        # Створюємо синопсис на основі перекладеного тексту
        text_for_summary = article.translated_text or article.translated_description or article.description
        
        if text_for_summary:
            summary = self.summarize_article(text_for_summary)
            if summary:
                article.summary = summary
        
        return article


def main():
    """Тестування сервісу перекладу"""
    import os
    from parse_news import SwissNewsParser
    
    # Налаштування логування
    logging.basicConfig(level=logging.INFO)
    
    # Перевіряємо API ключ
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️ Встановіть OPENAI_API_KEY для тестування")
        return
    
    print("🔄 Тестування сервісу перекладу")
    print("=" * 40)
    
    # Створюємо сервіс перекладу
    translator = TranslationService(api_key)
    
    # Тестові тексти різними мовами
    test_texts = {
        'de': "Die Schweiz unterstützt die Ukraine mit humanitärer Hilfe in Höhe von 50 Millionen Franken.",
        'fr': "La Suisse soutient l'Ukraine avec une aide humanitaire de 50 millions de francs.",
        'en': "Switzerland supports Ukraine with humanitarian aid worth 50 million francs."
    }
    
    for lang, text in test_texts.items():
        print(f"\n🌐 Тест перекладу з {translator._get_language_name(lang)} ({lang}):")
        print(f"Оригінал: {text}")
        
        translation = translator.translate_to_ukrainian(text, lang)
        if translation:
            print(f"Переклад: {translation}")
        else:
            print("❌ Помилка перекладу")
    
    # Тест синопсису
    print(f"\n📝 Тест створення синопсису:")
    test_article_text = """
    Швейцарський уряд оголосив про надання додаткової гуманітарної допомоги Україні 
    в розмірі 50 мільйонів швейцарських франків. Кошти будуть спрямовані на підтримку 
    біженців та відновлення критичної інфраструктури. Рішення було прийнято на 
    засіданні Федеральної ради у Берні в середу.
    """
    
    summary = translator.summarize_article(test_article_text.strip())
    if summary:
        print(f"Синопсис: {summary}")
    else:
        print("❌ Помилка створення синопсису")


if __name__ == "__main__":
    main()
