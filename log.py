from loguru import logger

logger.add(
    "log/app_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="10 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    encoding="utf-8",
)

__all__ = ["logger"]
