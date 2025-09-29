"""HTTP-клиент для Translation API (GET и POST)."""

import sys
import os
from typing import Any, Dict
import requests

# Добавляем путь к src в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONFIG


def build_headers() -> Dict[str, str]:
    """Строит заголовки для API.

    Принимаю:
        Ничего.

    Возвращаю:
        словарь заголовков с Accept и Content-Type.
    """
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def translate_text(api_url: str, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
    """Переводит текст с помощью выбранного API.

    Что делаю:
        Определяю тип API по URL и выполняю запрос перевода.

    Вход:
        api_url: URL конечной точки перевода (строка),
        text: текст для перевода (строка),
        source_lang: код исходного языка (например, 'en' или 'auto'),
        target_lang: код целевого языка (например, 'ru').

    Возвращаю:
        Словарь с результатом перевода или ошибкой.
    """
    try:
        headers = build_headers()

        if "libretranslate" in api_url:
            return _translate_libretranslate(api_url, headers, text, source_lang, target_lang)
        elif "mymemory" in api_url:
            return _translate_mymemory(api_url, headers, text, source_lang, target_lang)
        else:
            return {
                "error": "unknown_api",
                "message": "Unknown API type",
                "api": "Unknown",
                "status": "Unknown"
            }

    except requests.exceptions.RequestException as e:
        return {
            "error": "connection_error",
            "message": str(e),
            "url": api_url,
            "api": "Connection"
        }
    except Exception as e:
        return {
            "error": "unexpected_error",
            "message": str(e),
            "url": api_url,
            "api": "Unexpected"
        }


def _translate_libretranslate(api_url: str, headers: Dict[str, str],
                              text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
    """Переводит текст через LibreTranslate API.

    Что делаю:
        Отправляю POST запрос к LibreTranslate API (json-параметры).

    Вход:
        api_url: URL API (строка),
        headers: заголовки (словарь),
        text: текст для перевода (строка),
        source_lang: исходный язык (строка),
        target_lang: целевой язык (строка).

    Возвращаю:
        Результат перевода или ошибку (словарь).
    """
    payload = {
        "q": text,
        "source": source_lang,
        "target": target_lang,
        "format": "text"
    }

    resp = requests.post(api_url, headers=headers, json=payload, timeout=10)

    if resp.status_code == 200:
        result = resp.json()
        return {
            "translated_text": result.get("translatedText", ""),
            "source_language": result.get("detectedLanguage", {}).get("language", source_lang),
            "confidence": result.get("detectedLanguage", {}).get("confidence", 100),
            "api": "LibreTranslate"
        }
    else:
        return {
            "error": "api_error",
            "status": resp.status_code,
            "body": resp.text,
            "api": "LibreTranslate"
        }


def _translate_mymemory(api_url: str, headers: Dict[str, str],
                        text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
    """Переводит текст через MyMemory API.

    Что делаю:
        Отправляю GET запрос к MyMemory API.

    Вход:
        api_url: URL API (строка),
        headers: заголовки (словарь),
        text: текст для перевода (строка),
        source_lang: исходный язык (строка),
        target_lang: целевой язык (строка).

    Возвращаю:
        Результат перевода или ошибку (словарь).
    """
    params = {
        "q": text,
        "langpair": f"{source_lang}|{target_lang}"
    }

    resp = requests.get(api_url, headers=headers, params=params, timeout=10)

    if resp.status_code == 200:
        result = resp.json()
        if result.get("responseStatus") == 200:
            return {
                "translated_text": result.get("responseData", {}).get("translatedText", ""),
                "source_language": source_lang,
                "confidence": 100,
                "api": "MyMemory"
            }
        else:
            return {
                "error": "api_error",
                "status": result.get("responseStatus", 500),
                "body": result.get("responseDetails", "Unknown error"),
                "api": "MyMemory"
            }
    else:
        return {
            "error": "api_error",
            "status": resp.status_code,
            "body": resp.text,
            "api": "MyMemory"
        }