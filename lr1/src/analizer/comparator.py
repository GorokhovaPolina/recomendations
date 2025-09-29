"""Сравнение результатов переводов двух API."""

from typing import Dict, Any, List
import difflib


def compare_translations(translation_a: Dict[str, Any], translation_b: Dict[str, Any]) -> Dict[str, Any]:
    """Сравнивает результаты переводов двух API.

    Что делаю:
        Анализирую переводы с двух разных API и вычисляю метрики сравнения.

    Вход:
        translation_a: результат первого API (словарь),
        translation_b: результат второго API (словарь).

    Возвращаю:
        словарь с метриками сравнения:
            'similarity' (float) - схожесть переводов (0-1),
            'length_diff' (int) - разница в длине символов,
            'word_count_diff' (int) - разница в количестве слов,
            'api_a_name' (str) - название первого API,
            'api_b_name' (str) - название второго API,
            'both_successful' (bool) - успешны ли оба перевода,
            'confidence_diff' (int) - разница в уверенности API.
    """
    # Проверяем успешность переводов
    has_error_a = "error" in translation_a
    has_error_b = "error" in translation_b
    
    if has_error_a and has_error_b:
        return {
            "similarity": 0.0,
            "length_diff": 0,
            "word_count_diff": 0,
            "api_a_name": translation_a.get("api", "Unknown"),
            "api_b_name": translation_b.get("api", "Unknown"),
            "both_successful": False,
            "confidence_diff": 0,
            "error_message": "Оба API вернули ошибки"
        }
    
    if has_error_a or has_error_b:
        return {
            "similarity": 0.0,
            "length_diff": 0,
            "word_count_diff": 0,
            "api_a_name": translation_a.get("api", "Unknown"),
            "api_b_name": translation_b.get("api", "Unknown"),
            "both_successful": False,
            "confidence_diff": 0,
            "error_message": "Один из API вернул ошибку"
        }
    
    # Извлекаем переведенные тексты
    text_a = translation_a.get("translated_text", "")
    text_b = translation_b.get("translated_text", "")
    
    # Вычисляем метрики
    similarity = _calculate_similarity(text_a, text_b)
    length_diff = abs(len(text_a) - len(text_b))
    word_count_diff = abs(len(text_a.split()) - len(text_b.split()))
    confidence_diff = abs(translation_a.get("confidence", 0) - translation_b.get("confidence", 0))
    
    return {
        "similarity": similarity,
        "length_diff": length_diff,
        "word_count_diff": word_count_diff,
        "api_a_name": translation_a.get("api", "Unknown"),
        "api_b_name": translation_b.get("api", "Unknown"),
        "both_successful": True,
        "confidence_diff": confidence_diff,
        "text_a": text_a,
        "text_b": text_b,
        "source_language_a": translation_a.get("source_language", "Unknown"),
        "source_language_b": translation_b.get("source_language", "Unknown")
    }


def _calculate_similarity(text_a: str, text_b: str) -> float:
    """Вычисляет схожесть двух текстов.
    
    Что делаю:
        Использую SequenceMatcher для вычисления схожести текстов.
    
    Вход:
        text_a: первый текст (строка),
        text_b: второй текст (строка).
    
    Возвращаю:
        Коэффициент схожести от 0 до 1 (float).
    """
    if not text_a or not text_b:
        return 0.0
    
    # Нормализуем тексты для лучшего сравнения
    normalized_a = text_a.lower().strip()
    normalized_b = text_b.lower().strip()
    
    if normalized_a == normalized_b:
        return 1.0
    
    # Используем difflib для вычисления схожести
    matcher = difflib.SequenceMatcher(None, normalized_a, normalized_b)
    return matcher.ratio()


def get_translation_quality_score(translation: Dict[str, Any]) -> Dict[str, Any]:
    """Оценивает качество перевода.
    
    Что делаю:
        Анализирую различные аспекты качества перевода.
    
    Вход:
        translation: результат перевода (словарь).
    
    Возвращаю:
        Словарь с оценками качества (словарь).
    """
    if "error" in translation:
        return {
            "overall_score": 0,
            "confidence": 0,
            "has_error": True,
            "error_type": translation.get("error", "Unknown")
        }
    
    text = translation.get("translated_text", "")
    confidence = translation.get("confidence", 0)
    
    # Простые метрики качества
    word_count = len(text.split())
    char_count = len(text)
    
    # Базовый скор на основе уверенности API
    base_score = min(confidence / 100.0, 1.0)
    
    # Штраф за очень короткие или длинные переводы
    length_penalty = 0
    if word_count < 2:
        length_penalty = 0.2
    elif word_count > 100:
        length_penalty = 0.1
    
    # Штраф за пустые переводы
    if not text.strip():
        length_penalty = 1.0
    
    final_score = max(0, base_score - length_penalty)
    
    return {
        "overall_score": final_score,
        "confidence": confidence,
        "word_count": word_count,
        "char_count": char_count,
        "has_error": False,
        "api_name": translation.get("api", "Unknown")
    }
