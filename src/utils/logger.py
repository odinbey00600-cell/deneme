from __future__ import annotations

from loguru import logger


def configure_logger() -> None:
    logger.remove()
    logger.add(
        "logs/bot.log",
        level="INFO",
        rotation="50 MB",
        retention="14 days",
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )
    logger.add(lambda msg: print(msg, end=""), level="INFO")
