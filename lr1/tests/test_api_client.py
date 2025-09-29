"""Тесты для API клиента переводов."""

import pytest
from unittest.mock import patch, Mock
from src.api_client.rapidapi_client import translate_text, build_headers


class TestTranslationAPIClient:
    """Тесты для клиента API переводов."""

    def test_build_headers(self) -> None:
        """Тест создания заголовков.
        
        Что делаю:
            Проверяю, что build_headers создает правильные заголовки.
        
        Вход:
            Нет параметров.
        
        Возвращаю:
            Ничего (void).
        """
        host = "test-host.com"
        headers = build_headers(host)
        
        assert "Accept" in headers
        assert "Content-Type" in headers
        assert headers["Accept"] == "application/json"
        assert headers["Content-Type"] == "application/json"

    @patch('src.api_client.rapidapi_client.requests.post')
    def test_translate_libretranslate_success(self, mock_post: Mock) -> None:
        """Тест успешного перевода через LibreTranslate.
        
        Что делаю:
            Мокаю успешный ответ LibreTranslate API.
        
        Вход:
            mock_post: мок для requests.post.
        
        Возвращаю:
            Ничего (void).
        """
        # Настройка мока
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "translatedText": "Привет, как дела?",
            "detectedLanguage": {"language": "en", "confidence": 95}
        }
        mock_post.return_value = mock_response
        
        # Вызов функции
        result = translate_text(
            "https://libretranslate.com/translate",
            "libretranslate.com",
            "Hello, how are you?",
            "en",
            "ru"
        )
        
        # Проверки
        assert result["translated_text"] == "Привет, как дела?"
        assert result["source_language"] == "en"
        assert result["confidence"] == 95
        assert result["api"] == "LibreTranslate"
        mock_post.assert_called_once()

    @patch('src.api_client.rapidapi_client.requests.get')
    def test_translate_mymemory_success(self, mock_get: Mock) -> None:
        """Тест успешного перевода через MyMemory.
        
        Что делаю:
            Мокаю успешный ответ MyMemory API.
        
        Вход:
            mock_get: мок для requests.get.
        
        Возвращаю:
            Ничего (void).
        """
        # Настройка мока
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "responseStatus": 200,
            "responseData": {"translatedText": "Привет, как дела?"}
        }
        mock_get.return_value = mock_response
        
        # Вызов функции
        result = translate_text(
            "https://api.mymemory.translated.net/get",
            "api.mymemory.translated.net",
            "Hello, how are you?",
            "en",
            "ru"
        )
        
        # Проверки
        assert result["translated_text"] == "Привет, как дела?"
        assert result["source_language"] == "en"
        assert result["confidence"] == 100
        assert result["api"] == "MyMemory"
        mock_get.assert_called_once()

    @patch('src.api_client.rapidapi_client.requests.post')
    def test_translate_libretranslate_error(self, mock_post: Mock) -> None:
        """Тест обработки ошибки LibreTranslate API.
        
        Что делаю:
            Мокаю ответ с ошибкой от LibreTranslate API.
        
        Вход:
            mock_post: мок для requests.post.
        
        Возвращаю:
            Ничего (void).
        """
        # Настройка мока
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        # Вызов функции
        result = translate_text(
            "https://libretranslate.com/translate",
            "libretranslate.com",
            "Hello",
            "en",
            "ru"
        )
        
        # Проверки
        assert "error" in result
        assert result["status"] == 400
        assert result["body"] == "Bad Request"
        assert result["api"] == "LibreTranslate"

    @patch('src.api_client.rapidapi_client.requests.get')
    def test_translate_mymemory_error(self, mock_get: Mock) -> None:
        """Тест обработки ошибки MyMemory API.
        
        Что делаю:
            Мокаю ответ с ошибкой от MyMemory API.
        
        Вход:
            mock_get: мок для requests.get.
        
        Возвращаю:
            Ничего (void).
        """
        # Настройка мока
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "responseStatus": 500,
            "responseDetails": "Internal Server Error"
        }
        mock_get.return_value = mock_response
        
        # Вызов функции
        result = translate_text(
            "https://api.mymemory.translated.net/get",
            "api.mymemory.translated.net",
            "Hello",
            "en",
            "ru"
        )
        
        # Проверки
        assert "error" in result
        assert result["status"] == 500
        assert result["body"] == "Internal Server Error"
        assert result["api"] == "MyMemory"

    def test_translate_unknown_api(self) -> None:
        """Тест обработки неизвестного API.
        
        Что делаю:
            Проверяю обработку неизвестного типа API.
        
        Вход:
            Нет параметров.
        
        Возвращаю:
            Ничего (void).
        """
        result = translate_text(
            "https://unknown-api.com/translate",
            "unknown-api.com",
            "Hello",
            "en",
            "ru"
        )
        
        assert "error" in result
        assert result["error"] == "unknown_api"
        assert "Unknown API type" in result["message"]
