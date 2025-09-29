"""Простой скрипт для запуска приложения из корневой папки."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.run_app import main

if __name__ == "__main__":
    main()
