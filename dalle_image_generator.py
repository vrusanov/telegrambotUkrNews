"""
Модуль для генерації зображень через DALL-E API
Створює зображення на основі синопсису новин
"""

import os
import requests
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import openai
from datetime import datetime

logger = logging.getLogger(__name__)


class DALLEImageGenerator:
    """Клас для генерації зображень через DALL-E"""
    
    def __init__(self, api_key: str, images_dir: str = "images"):
        """
        Ініціалізація DALL-E генератора
        
        Args:
            api_key: OpenAI API ключ
            images_dir: Директорія для збереження зображень
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.images_dir = Path(images_dir)
        self.images_dir.mkdir(exist_ok=True)
    
    def generate_news_prompt(self, summary: str, style: str = "realistic photo") -> str:
        """
        Генерує промпт для DALL-E на основі синопсису новини
        
        Args:
            summary: Синопсис новини
            style: Стиль зображення
            
        Returns:
            Готовий промпт для DALL-E
        """
        # Базовий шаблон промпту
        base_prompt = f"Generate an image representing: {summary}. Style: {style}, journalistic, subtle colors, no faces, no text, professional news photography."
        
        # Додаткові налаштування для новинного стилю
        news_style_additions = [
            "official setting",
            "news-oriented", 
            "documentary style",
            "neutral perspective",
            "high quality",
            "professional lighting"
        ]
        
        # Об'єднуємо промпт
        full_prompt = f"{base_prompt} {', '.join(news_style_additions)}"
        
        # Обмежуємо довжину промпту (DALL-E має ліміт)
        if len(full_prompt) > 1000:
            full_prompt = full_prompt[:997] + "..."
        
        logger.info(f"Згенеровано промпт для DALL-E: {full_prompt[:100]}...")
        return full_prompt
    
    def generate_image(self, prompt: str, size: str = "1024x1024", 
                      quality: str = "standard") -> Optional[str]:
        """
        Генерує зображення через DALL-E API
        
        Args:
            prompt: Текстовий промпт для генерації
            size: Розмір зображення (1024x1024, 1792x1024, 1024x1792)
            quality: Якість зображення (standard, hd)
            
        Returns:
            URL згенерованого зображення або None
        """
        try:
            logger.info("Генеруємо зображення через DALL-E...")
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                n=1
            )
            
            if response.data:
                image_url = response.data[0].url
                logger.info("Зображення успішно згенеровано")
                return image_url
            else:
                logger.error("DALL-E не повернув зображення")
                return None
                
        except Exception as e:
            logger.error(f"Помилка генерації зображення DALL-E: {e}")
            return None
    
    def download_image(self, image_url: str, filename: str) -> Optional[str]:
        """
        Завантажує зображення з URL та зберігає локально
        
        Args:
            image_url: URL зображення
            filename: Ім'я файлу для збереження
            
        Returns:
            Шлях до збереженого файлу або None
        """
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Створюємо повний шлях до файлу
            file_path = self.images_dir / filename
            
            # Зберігаємо зображення
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Зображення збережено: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Помилка завантаження зображення: {e}")
            return None
    
    def generate_and_save_image(self, summary: str, filename: Optional[str] = None,
                               style: str = "realistic photo") -> Optional[str]:
        """
        Генерує зображення на основі синопсису та зберігає його
        
        Args:
            summary: Синопсис новини
            filename: Ім'я файлу (якщо None, генерується автоматично)
            style: Стиль зображення
            
        Returns:
            Шлях до збереженого зображення або None
        """
        # Генеруємо промпт
        prompt = self.generate_news_prompt(summary, style)
        
        # Генеруємо зображення
        image_url = self.generate_image(prompt)
        
        if not image_url:
            return None
        
        # Генеруємо ім'я файлу якщо не задано
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"news_image_{timestamp}.png"
        
        # Завантажуємо та зберігаємо зображення
        return self.download_image(image_url, filename)
    
    def generate_images_for_articles(self, articles_data: list) -> Dict[str, str]:
        """
        Генерує зображення для кількох статей
        
        Args:
            articles_data: Список словників з даними статей
            
        Returns:
            Словник {індекс_статті: шлях_до_зображення}
        """
        generated_images = {}
        
        for i, article in enumerate(articles_data):
            try:
                summary = article.get('summary', '')
                title = article.get('title', f'Article {i+1}')
                
                if not summary:
                    logger.warning(f"Пропускаємо статтю без синопсису: {title}")
                    continue
                
                logger.info(f"Генеруємо зображення для статті {i+1}: {title}")
                
                # Генеруємо ім'я файлу на основі індексу
                filename = f"news_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                
                # Генеруємо зображення
                image_path = self.generate_and_save_image(summary, filename)
                
                if image_path:
                    generated_images[str(i)] = image_path
                    logger.info(f"Зображення згенеровано для статті {i+1}")
                else:
                    logger.error(f"Не вдалося згенерувати зображення для статті {i+1}")
                
                # Затримка між запитами до API
                import time
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Помилка генерації зображення для статті {i+1}: {e}")
        
        logger.info(f"Згенеровано {len(generated_images)} зображень з {len(articles_data)} статей")
        return generated_images


def generate_image_for_news(summary: str, output_path: Optional[str] = None,
                          api_key: Optional[str] = None) -> Optional[str]:
    """
    Генерує зображення для новини
    
    Args:
        summary: Синопсис новини
        output_path: Шлях для збереження (якщо None, генерується автоматично)
        api_key: OpenAI API ключ (якщо None, береться з змінних середовища)
        
    Returns:
        Шлях до згенерованого зображення або None
    """
    if not api_key:
        api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        logger.error("OpenAI API ключ не налаштований")
        return None
    
    if not summary.strip():
        logger.error("Синопсис новини порожній")
        return None
    
    try:
        generator = DALLEImageGenerator(api_key)
        
        # Генеруємо ім'я файлу якщо не задано
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"news_image_{timestamp}.png"
        
        # Генеруємо зображення
        image_path = generator.generate_and_save_image(summary, output_path)
        
        if image_path:
            logger.info(f"Зображення успішно згенеровано: {image_path}")
            return image_path
        else:
            logger.error("Не вдалося згенерувати зображення")
            return None
            
    except Exception as e:
        logger.error(f"Помилка генерації зображення: {e}")
        return None


def create_news_prompt_variations(summary: str) -> list:
    """
    Створює варіації промптів для різних стилів новинних зображень
    
    Args:
        summary: Синопсис новини
        
    Returns:
        Список промптів для різних стилів
    """
    base_summary = summary.strip()
    
    prompt_variations = [
        # Реалістичний стиль
        f"Generate an image representing: {base_summary}. Style: realistic photo, journalistic, subtle colors, no faces, professional news photography.",
        
        # Документальний стиль
        f"Create a documentary-style image about: {base_summary}. Professional photography, neutral perspective, high quality, official setting.",
        
        # Мінімалістичний стиль
        f"Design a minimalist news illustration for: {base_summary}. Clean design, subtle colors, professional, no text, symbolic representation.",
        
        # Офіційний стиль
        f"Generate an official news image representing: {base_summary}. Formal setting, professional lighting, neutral colors, documentary style.",
        
        # Символічний стиль
        f"Create a symbolic representation of: {base_summary}. Abstract but clear, professional news style, subtle colors, no faces or text."
    ]
    
    return prompt_variations


# Приклад використання
if __name__ == "__main__":
    # Налаштування логування
    logging.basicConfig(level=logging.INFO)
    
    # Тестування DALL-E генератора
    api_key = os.getenv('OPENAI_API_KEY')
    
    if api_key:
        try:
            generator = DALLEImageGenerator(api_key)
            
            # Тестовий синопсис
            test_summary = "Швейцарія надає гуманітарну допомогу Україні в розмірі 50 мільйонів франків"
            
            # Генеруємо зображення
            image_path = generator.generate_and_save_image(
                summary=test_summary,
                filename="test_news_image.png"
            )
            
            if image_path:
                print(f"✅ Тестове зображення згенеровано: {image_path}")
            else:
                print("❌ Не вдалося згенерувати тестове зображення")
                
        except Exception as e:
            print(f"❌ Помилка тестування DALL-E: {e}")
    else:
        print("⚠️ Налаштуйте OPENAI_API_KEY для тестування DALL-E")
