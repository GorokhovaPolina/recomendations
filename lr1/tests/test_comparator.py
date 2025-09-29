"""Тесты для модуля сравнения переводов."""

import pytest
from src.analizer.comparator import compare_translations, get_translation_quality_score


class TestTranslationComparator:
    """Тесты для модуля сравнения переводов."""

    def test_compare_translations_successful(self) -> None:
        """Тест сравнения успешных переводов.
        
        Что делаю:
            Сравниваю два успешных перевода.
        
        Вход:
            Нет параметров.
        
        Возвращаю:
            Ничего (void).
        """
        translation_a = {
            "translated_text": "Привет, как дела?",
            "source_language": "en",
            "confidence": 95,
            "api": "LibreTranslate"
        }
        translation_b = {
            "translated_text": "Привет, как ты?",
            "source_language": "en",
            "confidence": 90,
            "api": "MyMemory"
        }
        
        result = compare_translations(translation_a, translation_b)
        
        assert result["both_successful"] is True
        assert result["api_a_name"] == "LibreTranslate"
        assert result["api_b_name"] == "MyMemory"
        assert result["similarity"] > 0.5  # Переводы должны быть похожи
        assert result["confidence_diff"] == 5

    def test_compare_translations_identical(self) -> None:
        """Тест сравнения идентичных переводов.
        
        Что делаю:
            Сравниваю два одинаковых перевода.
        
        Вход:
            Нет параметров.
        
        Возвращаю:
            Ничего (void).
        """
        translation_a = {
            "translated_text": "Привет, как дела?",
            "source_language": "en",
            "confidence": 95,
            "api": "LibreTranslate"
        }
        translation_b = {
            "translated_text": "Привет, как дела?",
            "source_language": "en",
            "confidence": 95,
            "api": "MyMemory"
        }
        
        result = compare_translations(translation_a, translation_b)
        
        assert result["both_successful"] is True
        assert result["similarity"] == 1.0
        assert result["length_diff"] == 0
        assert result["word_count_diff"] == 0
        assert result["confidence_diff"] == 0

    def test_compare_translations_with_error(self) -> None:
        """Тест сравнения переводов с ошибкой.
        
        Что делаю:
            Сравниваю перевод с ошибкой и успешный перевод.
        
        Вход:
            Нет параметров.
        
        Возвращаю:
            Ничего (void).
        """
        translation_a = {
            "error": "api_error",
            "status": 500,
            "api": "LibreTranslate"
        }
        translation_b = {
            "translated_text": "Привет, как дела?",
            "source_language": "en",
            "confidence": 95,
            "api": "MyMemory"
        }
        
        result = compare_translations(translation_a, translation_b)
        
        assert result["both_successful"] is False
        assert "error_message" in result
        assert "Один из API вернул ошибку" in result["error_message"]

    def test_compare_translations_both_errors(self) -> None:
        """Тест сравнения переводов с ошибками в обоих API.
        
        Что делаю:
            Сравниваю два перевода с ошибками.
        
        Вход:
            Нет параметров.
        
        Возвращаю:
            Ничего (void).
        """
        translation_a = {
            "error": "api_error",
            "status": 500,
            "api": "LibreTranslate"
        }
        translation_b = {
            "error": "connection_error",
            "message": "Connection failed",
            "api": "MyMemory"
        }
        
        result = compare_translations(translation_a, translation_b)
        
        assert result["both_successful"] is False
        assert "Оба API вернули ошибки" in result["error_message"]

    def test_get_translation_quality_score_successful(self) -> None:
        """Тест оценки качества успешного перевода.
        
        Что делаю:
            Оцениваю качество успешного перевода.
        
        Вход:
            Нет параметров.
        
        Возвращаю:
            Ничего (void).
        """
        translation = {
            "translated_text": "Привет, как дела?",
            "source_language": "en",
            "confidence": 95,
            "api": "LibreTranslate"
        }
        
        result = get_translation_quality_score(translation)
        
        assert result["has_error"] is False
        assert result["overall_score"] > 0.8
        assert result["confidence"] == 95
        assert result["word_count"] == 3
        assert result["api_name"] == "LibreTranslate"

    def test_get_translation_quality_score_with_error(self) -> None:
        """Тест оценки качества перевода с ошибкой.
        
        Что делаю:
            Оцениваю качество перевода с ошибкой.
        
        Вход:
            Нет параметров.
        
        Возвращаю:
            Ничего (void).
        """
        translation = {
            "error": "api_error",
            "status": 500,
            "api": "LibreTranslate"
        }
        
        result = get_translation_quality_score(translation)
        
        assert result["has_error"] is True
        assert result["overall_score"] == 0
        assert result["confidence"] == 0
        assert result["error_type"] == "api_error"

    def test_get_translation_quality_score_empty_text(self) -> None:
        """Тест оценки качества пустого перевода.
        
        Что делаю:
            Оцениваю качество пустого перевода.
        
        Вход:
            Нет параметров.
        
        Возвращаю:
            Ничего (void).
        """
        translation = {
            "translated_text": "",
            "source_language": "en",
            "confidence": 50,
            "api": "LibreTranslate"
        }
        
        result = get_translation_quality_score(translation)
        
        assert result["has_error"] is False
        assert result["overall_score"] == 0  # Пустой текст должен давать 0
        assert result["word_count"] == 0
