"""Qt GUI: окно для сравнения переводов с двух разных API."""

import sys
import os
import json
from typing import Any
from PySide6 import QtWidgets, QtCore

# Добавляем путь к src в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_client.rapidapi_client import translate_text
from config import CONFIG
from analizer.comparator import compare_translations, get_translation_quality_score


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Translation API Comparator — Сравнение переводов")
        self.resize(1200, 900)
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        # Заголовок
        title_label = QtWidgets.QLabel("Сравнение переводов с разных API")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin: 10px;")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title_label)

        # Ввод текста
        input_group = QtWidgets.QGroupBox("Ввод текста для перевода")
        input_layout = QtWidgets.QVBoxLayout(input_group)
        
        self.text_input = QtWidgets.QPlainTextEdit()
        self.text_input.setPlaceholderText("Введите текст для перевода...")
        self.text_input.setMaximumHeight(100)
        input_layout.addWidget(self.text_input)

        # Выбор языков
        lang_layout = QtWidgets.QHBoxLayout()
        
        # Исходный язык
        lang_layout.addWidget(QtWidgets.QLabel("Исходный язык:"))
        self.source_lang = QtWidgets.QComboBox()
        self.source_lang.addItems(["auto", "en", "ru", "es", "fr", "de", "it", "pt", "ja", "ko", "zh"])
        self.source_lang.setCurrentText("en")
        lang_layout.addWidget(self.source_lang)
        
        # Стрелка
        lang_layout.addWidget(QtWidgets.QLabel("→"))
        
        # Целевой язык
        lang_layout.addWidget(QtWidgets.QLabel("Целевой язык:"))
        self.target_lang = QtWidgets.QComboBox()
        self.target_lang.addItems(["ru", "en", "es", "fr", "de", "it", "pt", "ja", "ko", "zh"])
        self.target_lang.setCurrentText("ru")
        lang_layout.addWidget(self.target_lang)
        
        # Кнопка перевода
        self.btn_translate = QtWidgets.QPushButton("Перевести и сравнить")
        self.btn_translate.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.btn_translate.clicked.connect(self.on_translate)
        lang_layout.addWidget(self.btn_translate)
        
        input_layout.addLayout(lang_layout)
        layout.addWidget(input_group)

        # Статус
        self.status_label = QtWidgets.QLabel("Готов к переводу")
        self.status_label.setStyleSheet("color: green; font-weight: bold; padding: 5px;")
        layout.addWidget(self.status_label)

        # Результаты переводов
        results_layout = QtWidgets.QHBoxLayout()
        
        # API 1 (LibreTranslate)
        api1_group = QtWidgets.QGroupBox("LibreTranslate API")
        api1_layout = QtWidgets.QVBoxLayout(api1_group)
        self.text_api1 = QtWidgets.QPlainTextEdit()
        self.text_api1.setReadOnly(True)
        self.text_api1.setMaximumHeight(200)
        api1_layout.addWidget(self.text_api1)
        
        # Качество API 1
        self.quality_api1 = QtWidgets.QLabel("Ожидание перевода...")
        self.quality_api1.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        api1_layout.addWidget(self.quality_api1)
        
        results_layout.addWidget(api1_group)
        
        # API 2 (MyMemory)
        api2_group = QtWidgets.QGroupBox("MyMemory API")
        api2_layout = QtWidgets.QVBoxLayout(api2_group)
        self.text_api2 = QtWidgets.QPlainTextEdit()
        self.text_api2.setReadOnly(True)
        self.text_api2.setMaximumHeight(200)
        api2_layout.addWidget(self.text_api2)
        
        # Качество API 2
        self.quality_api2 = QtWidgets.QLabel("Ожидание перевода...")
        self.quality_api2.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        api2_layout.addWidget(self.quality_api2)
        
        results_layout.addWidget(api2_group)
        
        layout.addLayout(results_layout)

        # Сравнение
        comparison_group = QtWidgets.QGroupBox("Результаты сравнения")
        comparison_layout = QtWidgets.QVBoxLayout(comparison_group)
        self.comparison_text = QtWidgets.QLabel("Введите текст и нажмите 'Перевести и сравнить'")
        self.comparison_text.setStyleSheet("""
            font-size: 14px; 
            padding: 15px; 
            background-color: #ecf0f1; 
            border-radius: 5px;
            border: 1px solid #bdc3c7;
        """)
        self.comparison_text.setWordWrap(True)
        comparison_layout.addWidget(self.comparison_text)
        layout.addWidget(comparison_group)

    def on_translate(self) -> None:
        """Обработчик нажатия кнопки перевода.
        
        Что делаю:
            Получаю переводы с двух API и сравниваю их.
        
        Вход:
            Нет параметров.
        
        Возвращаю:
            Ничего (void).
        """
        text = self.text_input.toPlainText().strip()
        if not text:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Введите текст для перевода")
            return

        source_lang = self.source_lang.currentText()
        target_lang = self.target_lang.currentText()

        self.status_label.setText("Переводим...")
        self.status_label.setStyleSheet("color: blue; font-weight: bold; padding: 5px;")
        self.btn_translate.setEnabled(False)
        
        # Очищаем предыдущие результаты
        self.text_api1.clear()
        self.text_api2.clear()
        self.quality_api1.setText("Переводим...")
        self.quality_api2.setText("Переводим...")
        self.comparison_text.setText("Выполняется перевод...")

        try:
            # Получаем переводы из API
            translation_a = translate_text(CONFIG.api1_url, text, source_lang, target_lang)
            translation_b = translate_text(CONFIG.api2_url, text, source_lang, target_lang)

            # Отображаем результаты
            self.text_api1.setPlainText(self._format_translation(translation_a))
            self.text_api2.setPlainText(self._format_translation(translation_b))
            
            # Оценка качества
            quality_a = get_translation_quality_score(translation_a)
            quality_b = get_translation_quality_score(translation_b)
            
            self.quality_api1.setText(self._format_quality(quality_a))
            self.quality_api2.setText(self._format_quality(quality_b))
            
            # Сравнение переводов
            comparison = compare_translations(translation_a, translation_b)
            self.comparison_text.setText(self._format_comparison(comparison))
            
            if comparison.get("both_successful", False):
                self.status_label.setText("Перевод завершен успешно")
                self.status_label.setStyleSheet("color: green; font-weight: bold; padding: 5px;")
            else:
                self.status_label.setText("Ошибка при переводе")
                self.status_label.setStyleSheet("color: red; font-weight: bold; padding: 5px;")
                
        except Exception as e:
            self.comparison_text.setText(f"Произошла ошибка: {str(e)}")
            self.status_label.setText("Произошла ошибка")
            self.status_label.setStyleSheet("color: red; font-weight: bold; padding: 5px;")
        finally:
            self.btn_translate.setEnabled(True)


    def _format_translation(self, translation: dict) -> str:
        """Форматирует результат перевода для отображения.
        
        Что делаю:
            Преобразую словарь перевода в читаемый текст.
        
        Вход:
            translation: результат перевода (словарь).
        
        Возвращаю:
            Отформатированную строку (строка).
        """
        if "error" in translation:
            return f"❌ Ошибка: {translation.get('error', 'Unknown error')}\n" \
                   f"Статус: {translation.get('status', 'Unknown')}\n" \
                   f"API: {translation.get('api', 'Unknown')}"
        
        return f"✅ {translation.get('translated_text', '')}\n\n" \
               f"Исходный язык: {translation.get('source_language', 'Unknown')}\n" \
               f"Уверенность: {translation.get('confidence', 0)}%\n" \
               f"API: {translation.get('api', 'Unknown')}"

    def _format_quality(self, quality: dict) -> str:
        """Форматирует оценку качества перевода.
        
        Что делаю:
            Преобразую метрики качества в читаемый текст.
        
        Вход:
            quality: метрики качества (словарь).
        
        Возвращаю:
            Отформатированную строку (строка).
        """
        if quality.get("has_error", False):
            return f"❌ Ошибка: {quality.get('error_type', 'Unknown')}"
        
        score = quality.get("overall_score", 0)
        confidence = quality.get("confidence", 0)
        word_count = quality.get("word_count", 0)
        
        # Цветовая индикация качества
        if score >= 0.8:
            color = "green"
            emoji = "🟢"
        elif score >= 0.6:
            color = "orange"
            emoji = "🟡"
        else:
            color = "red"
            emoji = "🔴"
        
        return f"{emoji} Качество: {score:.1%} | Уверенность: {confidence}% | Слов: {word_count}"

    def _format_comparison(self, comparison: dict) -> str:
        """Форматирует результаты сравнения переводов.
        
        Что делаю:
            Преобразую метрики сравнения в читаемый текст.
        
        Вход:
            comparison: результаты сравнения (словарь).
        
        Возвращаю:
            Отформатированную строку (строка).
        """
        if not comparison.get("both_successful", False):
            return f"❌ {comparison.get('error_message', 'Ошибка сравнения')}"
        
        similarity = comparison.get("similarity", 0)
        length_diff = comparison.get("length_diff", 0)
        word_count_diff = comparison.get("word_count_diff", 0)
        confidence_diff = comparison.get("confidence_diff", 0)
        
        # Определяем уровень схожести
        if similarity >= 0.9:
            similarity_text = "🟢 Очень похожи"
        elif similarity >= 0.7:
            similarity_text = "🟡 Похожи"
        elif similarity >= 0.5:
            similarity_text = "🟠 Частично похожи"
        else:
            similarity_text = "🔴 Различаются"
        
        return f"""
        <h3>📈 Анализ переводов</h3>
        <p><b>Схожесть:</b> {similarity_text} ({similarity:.1%})</p>
        <p><b>Разница в длине:</b> {length_diff} символов</p>
        <p><b>Разница в словах:</b> {word_count_diff} слов</p>
        <p><b>Разница в уверенности:</b> {confidence_diff}%</p>
        <p><b>API 1:</b> {comparison.get('api_a_name', 'Unknown')}</p>
        <p><b>API 2:</b> {comparison.get('api_b_name', 'Unknown')}</p>
        """
