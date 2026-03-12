import sys
import os
import logging
from loguru import logger
from typing import Optional


LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:"
    "<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)

LOG_FORMAT_FILE = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
    "{level: <8} | "
    "{name}:{function}:{line} | "
    "{message}"
)

_initialized = False


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def _default_filter(record):
    if "module" not in record["extra"]:
        record["extra"]["module"] = record["name"]
    return True


def setup_logging(
    level: str = "INFO",
    log_dir: str = "./logs",
    log_file_max_size: str = "10 MB",
    log_file_retention: str = "7 days",
    console_enabled: bool = True,
    file_enabled: bool = True,
    json_enabled: bool = False,
) -> None:
    global _initialized

    if _initialized:
        return

    logger.remove()

    if console_enabled:
        logger.add(
            sys.stdout,
            level=level,
            format=LOG_FORMAT,
            colorize=True,
            enqueue=True,
            filter=_default_filter,
        )

    if file_enabled:
        os.makedirs(log_dir, exist_ok=True)

        logger.add(
            os.path.join(log_dir, "xivmind.log"),
            level=level,
            format=LOG_FORMAT_FILE,
            rotation=log_file_max_size,
            retention=log_file_retention,
            compression="zip",
            enqueue=True,
            encoding="utf-8",
            filter=_default_filter,
        )

        logger.add(
            os.path.join(log_dir, "xivmind.error.log"),
            level="ERROR",
            format=LOG_FORMAT_FILE,
            rotation=log_file_max_size,
            retention=log_file_retention,
            compression="zip",
            enqueue=True,
            encoding="utf-8",
            filter=_default_filter,
        )

    if json_enabled:
        logger.add(
            os.path.join(log_dir, "xivmind.json.log"),
            level=level,
            serialize=True,
            rotation=log_file_max_size,
            retention=log_file_retention,
            enqueue=True,
            encoding="utf-8",
            filter=_default_filter,
        )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    for name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers = [InterceptHandler()]
        uvicorn_logger.propagate = False

    for name in ["httpx", "httpcore", "multipart", "watchfiles"]:
        third_party_logger = logging.getLogger(name)
        third_party_logger.handlers = [InterceptHandler()]
        third_party_logger.setLevel(logging.WARNING)

    _initialized = True
    logger.info("Logging system initialized")


def setup_logging_from_settings() -> None:
    from app.config import get_settings

    settings = get_settings()
    setup_logging(
        level=settings.LOG_LEVEL,
        log_dir=settings.LOG_DIR,
        log_file_max_size=settings.LOG_FILE_MAX_SIZE,
        log_file_retention=settings.LOG_FILE_RETENTION,
        console_enabled=settings.LOG_CONSOLE_ENABLED,
        file_enabled=settings.LOG_FILE_ENABLED,
        json_enabled=settings.LOG_JSON_ENABLED,
    )


def get_logger(module_name: Optional[str] = None):
    if module_name:
        return logger.bind(module=module_name)
    return logger
