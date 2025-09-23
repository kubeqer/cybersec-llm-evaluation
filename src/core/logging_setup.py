import sys
from datetime import datetime
from pathlib import Path

from loguru import logger

from src.core.paths import LOGS_DIR


def logging_setup(
    level: str = "INFO",
    format: str | None = None,
    stderr: bool = True,
    file_path: Path | None = None,
    rotation: str | None = "100 MB",
) -> None:
    logger.remove()
    if format is None:
        format = "{time:DD-MM-YYYY HH:mm:ss} | {level: <8} | {message}"
    if stderr:
        logger.add(
            sys.stderr,
            level=level,
            format=format,
            colorize=True,
            backtrace=True,
            diagnose=True,
            enqueue=True,
        )
    if file_path:
        logger.add(
            file_path,
            level=level,
            format=format,
            rotation=rotation,
        )


def configure_basic_logging() -> None:
    logging_setup(file_path=LOGS_DIR / datetime.now().strftime("%Y%m%d_%H%M%S"))
