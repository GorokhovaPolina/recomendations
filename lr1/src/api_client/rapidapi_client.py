"""HTTP-клиент для Translation API (GET и POST)."""

import os
import requests
from typing import Any, Dict
from urllib.parse import quote
from config import CONFIG


def build_headers() -> Dict[str, str]:
    """Строит заголовки для API."""
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def _detect_api_type(api_url: str) -> str:
    """Определяет тип API по URL.

    Вход:
        api_url: строка с URL.

    Возвращаю:
        'mymemory' для MyMemory,
        'lingva' для Lingva Translate,
        'unknown' если не удалось определить.
    """
    url = api_url.lower()
    if "mymemory" in url:
        return "mymemory"
    if "lingva" in url:
        return "lingva"
    return "unknown"


def translate_text(api_url: str, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
    """Переводит текст с помощью выбранного API.

    Что делаю:
        Определяю тип API и вызываю соответствующую функцию перевода.

    Вход:
        api_url: URL конечной точки перевода,
        text: текст для перевода,
        source_lang: исходный язык,
        target_lang: целевой язык.

    Возвращаю:
        Словарь с результатом перевода или ошибкой.
    """
    if not api_url:
        return {"error": "empty_url", "message": "API URL не указан", "api": "Unknown", "status": "Invalid URL"}

    api_type = _detect_api_type(api_url)
    headers = build_headers()

    try:
        if api_type == "mymemory":
            return _translate_mymemory(api_url, headers, text, source_lang, target_lang)
        if api_type == "lingva":
            return _translate_lingva(api_url, headers, text, source_lang, target_lang)

        return {"error": "unknown_api", "message": "Cannot determine API type from URL", "api": "Unknown", "status": "Unknown"}

    except requests.exceptions.RequestException as e:
        return {"error": "request_failed", "message": str(e), "api": api_type}
    except Exception as e:
        return {"error": "unexpected_error", "message": str(e), "api": api_type}


def _translate_mymemory(api_url: str, headers: Dict[str, str], text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
    """Перевод через MyMemory API.

    Что делаю:
        Отправляю GET запрос к MyMemory с параметрами langpair.

    Вход:
        api_url: URL API,
        headers: заголовки,
        text: текст,
        source_lang: исходный язык,
        target_lang: целевой язык.

    Возвращаю:
        Словарь с переведённым текстом или ошибкой.
    """
    params = {"q": text, "langpair": f"{source_lang}|{target_lang}"}

    try:
        resp = requests.get(api_url, headers=headers, params=params, timeout=10)
        if resp.status_code == 200:
            result = resp.json()
            if result.get("responseStatus") == 200:
                return {"translated_text": result.get("responseData", {}).get("translatedText", ""),
                        "source_language": source_lang, "confidence": 100, "api": "MyMemory"}
            else:
                return {"error": "api_error", "message": f"MyMemory API error: {result.get('responseDetails','Unknown error')}",
                        "status": result.get("responseStatus", 500), "body": result.get("responseDetails", "Unknown error"), "api": "MyMemory"}
        else:
            return {"error": "api_error", "message": f"HTTP error {resp.status_code}", "status": resp.status_code, "body": resp.text, "api": "MyMemory"}

    except requests.exceptions.RequestException as exc:
        return {"error": "request_failed", "message": str(exc), "api": "MyMemory"}


def _translate_lingva(api_url: str, headers: Dict[str, str], text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
    """Перевод через Lingva Translate.

    Что делаю:
        Отправляю GET запрос к публичному Lingva API, URL-кодирую текст.

    Вход:
        api_url: URL API,
        headers: заголовки,
        text: текст,
        source_lang: исходный язык,
        target_lang: целевой язык.

    Возвращаю:
        Словарь с переведённым текстом или ошибкой.
    """
    text = (text or "").strip()
    if not text:
        return {"error": "empty_text", "message": "Текст пустой", "api": "Lingva"}

    encoded_text = quote(text)
    url = f"{api_url}/{source_lang}/{target_lang}/{encoded_text}"

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            result = resp.json()
            translated = result.get("translation", "")
            return {"translated_text": translated, "source_language": source_lang, "confidence": 100, "api": "Lingva"}
        else:
            return {"error": "api_error", "message": f"Lingva вернул код {resp.status_code}", "status": resp.status_code, "body": resp.text, "api": "Lingva"}

    except requests.exceptions.RequestException as exc:
        return {"error": "request_failed", "message": str(exc), "api": "Lingva"}
    except ValueError:
        return {"error": "invalid_json", "message": "Некорректный JSON", "api": "Lingva"}


# Быстрая отладка
if __name__ == "__main__":
    print("Тест MyMemory...")
    out1 = translate_text(MYMEMORY_URL, "Hello, how are you?", "en", "fr")
    print(out1)

    print("Тест Lingva...")
    out2 = translate_text(LINGVA_URL, "Hello, how are you?", "en", "fr")
    print(out2)