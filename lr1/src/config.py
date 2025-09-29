"""Загрузка конфигурации из .env"""

from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    """Конфигурация приложения.

    Все поля читаются из .env.
    """
    api1_url: str = os.getenv("LINGVA_URL", "")
    api2_url: str = os.getenv("MYMEMORY_URL", "")


CONFIG = Config()