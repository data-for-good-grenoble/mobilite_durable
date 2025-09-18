import json
import logging

import src.settings as settings


class JsonlFormatter(logging.Formatter):
    def format(self, record) -> str:
        return json.dumps(self.get_log_entry(record))

    def get_log_entry(self, record) -> dict:
        return {
            "timestamp": self.formatTime(record),
            "levelname": record.levelname,
            "name": f"{record.name}|{record.funcName}:{record.lineno}",
            "message": record.getMessage(),
            **record.__dict__.get("extra", {}),
        }


def setup_logger(
    level: int = settings.LOGGER_LEVEL,
    datefmt: str = "%Y-%m-%d %H:%M:%S",
    format: str = "%(asctime)s - %(levelname)s - %(name)s|%(funcName)s:%(lineno)d - %(message)s",
    name: str = "main",
):
    """Configuration globale du logger"""
    # Use root logger if no specified name
    logger = logging.getLogger() if name == "main" else logging.getLogger(name)
    logger.setLevel(level)

    # Avoid handler duplication
    if logger.hasHandlers():
        return logger

    # logger console
    log_console = logging.StreamHandler()
    log_console.setFormatter(logging.Formatter(format))
    logger.addHandler(log_console)

    # logger classique
    log_handler = logging.FileHandler("errors.log", encoding="utf-8")
    log_handler.setFormatter(logging.Formatter(format, datefmt=datefmt))
    logger.addHandler(log_handler)

    # logger JsonL
    jsonl_handler = logging.FileHandler("errors.jsonl", encoding="utf-8")
    jsonl_handler.setFormatter(JsonlFormatter(datefmt=datefmt))
    logger.addHandler(jsonl_handler)

    return logger
