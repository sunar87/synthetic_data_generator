import os
import logging
from logging.handlers import TimedRotatingFileHandler


def get_logger(name: str) -> logging.Logger:
    """
    Возвращает настроенный логгер для проекта.
    Все модули должны вызывать get_logger(__name__).
    """
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    handler = TimedRotatingFileHandler(
        filename="logs/app.log",
        when="midnight",
        backupCount=7,
        encoding="utf-8",
    )

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    return logger
