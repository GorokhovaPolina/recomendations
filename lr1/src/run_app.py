#!/usr/bin/env python3
"""Главный файл для запуска приложения Pokemon API Comparator."""

import sys
import os
from PySide6.QtWidgets import QApplication

# Добавляем путь к src в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow


def main() -> None:
    """Запускает GUI приложение.
    
    Что делаю:
        Создаю QApplication и MainWindow, запускаю главный цикл.
    
    Вход:
        Нет параметров.
    
    Возвращаю:
        Ничего (void).
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
